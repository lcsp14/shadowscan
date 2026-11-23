"""Testes das funções puras (sem rede). Rodar: python -m unittest discover tests"""

import unittest

from shadowscan.classify import ADMIN, DEBUG, OUTRO, VERSAO, classify
from shadowscan.diff import compute_diff, matches_template
from shadowscan.discovery import Observation, literal_prefixes, version_variants
from shadowscan.ground_truth import degrade
from shadowscan.metrics import evaluate
from shadowscan.responses import Resp, same_response
from shadowscan.spec_parser import Endpoint, parse_spec

SPEC = {
    "openapi": "3.0.0",
    "servers": [{"url": "http://x/api"}],
    "paths": {
        "/users": {"get": {}, "post": {}},
        "/users/{id}": {"get": {}, "delete": {}, "parameters": []},
        "/v2/items/": {"get": {}},
    },
}


def obs(m, p, tpl=None, origem="wordlist"):
    return Observation(m, p, tpl, origem, 200)


class TestParser(unittest.TestCase):
    def test_extrai_metodos_com_prefixo_e_normaliza(self):
        d = parse_spec(SPEC)
        self.assertIn(Endpoint("GET", "/api/users/{id}"), d)
        self.assertIn(Endpoint("GET", "/api/v2/items"), d)  # barra final removida
        self.assertEqual(len(d), 5)  # "parameters" não é método


class TestMatching(unittest.TestCase):
    def test_template(self):
        self.assertTrue(matches_template("/users/42", "/users/{id}"))
        self.assertFalse(matches_template("/users/42/x", "/users/{id}"))
        self.assertFalse(matches_template("/posts/42", "/users/{id}"))

    def test_diff_shadow_zombie(self):
        d = {Endpoint("GET", "/users"), Endpoint("GET", "/users/{id}"), Endpoint("GET", "/old")}
        o = [obs("GET", "/users"), obs("GET", "/users/1", "/users/{id}", "declarado"),
             obs("DELETE", "/users"), obs("GET", "/admin")]
        r = compute_diff(d, o)
        self.assertEqual({(s.method, s.path) for s in r.shadow}, {("DELETE", "/users"), ("GET", "/admin")})
        self.assertEqual(r.zombie, [Endpoint("GET", "/old")])

    def test_ambiguo_politica(self):
        d = {Endpoint("GET", "/users/{id}")}
        o = [obs("GET", "/users/admin")]
        self.assertEqual(compute_diff(d, o, "declarado").shadow, [])
        self.assertEqual(len(compute_diff(d, o, "shadow").shadow), 1)

    def test_nome_do_parametro_irrelevante(self):
        d = {Endpoint("GET", "/books/{book_title}")}
        r = compute_diff(d, [obs("GET", "/books/{param}", "/books/{param}", "coringa")])
        self.assertEqual(r.shadow, [])


class TestDiscoveryHelpers(unittest.TestCase):
    def test_prefixos(self):
        self.assertEqual(literal_prefixes("/users/v1/{u}/email"), ["/users", "/users/v1"])

    def test_raiz_sempre_candidata(self):
        # Regressão do defeito E13/D18: "/" fora da spec ainda precisa ser sondada.
        from shadowscan.discovery import build_candidates
        cands = build_candidates({Endpoint("GET", "/users/v1")}, ["admin"], "1")
        self.assertIn("/", {c.path for c in cands})

    def test_versoes(self):
        self.assertEqual(version_variants("/api/v2/x"), ["/api/v1/x", "/api/v3/x"])


class TestSoft404(unittest.TestCase):
    def test_eco_do_caminho_e_ignorado(self):
        a = Resp("GET", "/zzabc123", 200, "application/json", '{"error":"route /zzabc123 not found"}')
        b = Resp("GET", "/admin", 200, "application/json", '{"error":"route /admin not found"}')
        self.assertTrue(same_response(a, b))

    def test_status_diferente(self):
        a = Resp("GET", "/a", 404, "", "x")
        b = Resp("GET", "/b", 200, "", "x")
        self.assertFalse(same_response(a, b))


class TestClassify(unittest.TestCase):
    def test_categorias(self):
        from shadowscan.diff import Shadow
        d = {Endpoint("GET", "/api/v2/users")}
        mk = lambda p: Shadow("GET", p, "x", 200)
        self.assertEqual(classify(mk("/api/v1/users"), d), VERSAO)
        self.assertEqual(classify(mk("/api/_debug"), d), DEBUG)
        self.assertEqual(classify(mk("/admin/users"), d), ADMIN)
        self.assertEqual(classify(mk("/foo"), d), OUTRO)


class TestGroundTruthEMetricas(unittest.TestCase):
    def test_degrade_reprodutivel_e_tipo(self):
        _, r1 = degrade(SPEC, 2, seed=7)
        _, r2 = degrade(SPEC, 2, seed=7)
        self.assertEqual(r1, r2)
        _, todos = degrade(SPEC, 5, seed=0)
        self.assertTrue(all(r["tipo"] == "caminho" for r in todos))

    def test_metricas(self):
        from shadowscan.diff import Shadow
        rep = [Shadow("GET", "/a", "x", 200), Shadow("GET", "/b", "x", 200), Shadow("GET", "/real", "x", 200)]
        gt = [{"method": "GET", "path": "/a", "tipo": "caminho"}, {"method": "GET", "path": "/c", "tipo": "caminho"}]
        m = evaluate(rep, gt, intrinsecos=["GET /real"])
        self.assertEqual((m["vp"], m["fp"], m["fn"]), (1, 1, 1))
        self.assertAlmostEqual(m["f1"], 0.5)


if __name__ == "__main__":
    unittest.main()


class TestRenovacaoAuth(unittest.TestCase):
    """D19 / E22: renovação periódica de credencial."""

    def test_sem_provedor_headers_fixos(self):
        import asyncio
        from shadowscan.discovery import Discoverer
        d = Discoverer("http://x", set(), [], headers={"A": "1"})
        asyncio.run(d.maybe_refresh_auth())
        self.assertEqual(d.headers, {"A": "1"})
        self.assertEqual(d.result.renovacoes_auth, 0)

    def test_com_provedor_renova_quando_vence(self):
        import asyncio
        from shadowscan.discovery import Discoverer
        n = iter(range(100))
        d = Discoverer("http://x", set(), [], headers={}, auth_refresh=lambda: {"T": str(next(n))},
                       refresh_every=1000)
        async def go():
            await d.maybe_refresh_auth()   # primeira chamada: renova
            await d.maybe_refresh_auth()   # dentro do intervalo: não renova
            d._last_refresh -= 2000        # simula o intervalo vencido
            await d.maybe_refresh_auth()
        asyncio.run(go())
        self.assertEqual(d.headers, {"T": "1"})
        self.assertEqual(d.result.renovacoes_auth, 2)


class TestNormalizacaoSimetrica(unittest.TestCase):
    """D20 / E27: segmento pedido coincidente com palavra do corpo de erro."""

    def test_segmento_igual_a_chave_json(self):
        corpo = '{ "status": "fail", "message": "User not found"}'
        base = Resp("GET", "/users/v1/zzq1w2e3r4", 404, "", corpo)
        for seg in ("message", "status", "fail", "found"):
            with self.subTest(seg=seg):
                self.assertTrue(same_response(Resp("GET", f"/users/v1/{seg}", 404, "", corpo), base))

    def test_resposta_realmente_diferente_continua_diferente(self):
        base = Resp("GET", "/users/v1/zzq1w2e3r4", 404, "", '{ "status": "fail", "message": "User not found"}')
        real = Resp("GET", "/users/v1/admin", 404, "", '{"username": "admin", "email": "admin@mail.com"}')
        self.assertFalse(same_response(real, base))


class TestAgrupamentoTemplateObservado(unittest.TestCase):
    """D21 / E27: literal que casa com template inferido (não declarado) não vira 2º shadow."""

    def test_literal_agrupado_no_coringa(self):
        d = {Endpoint("GET", "/users/v1")}
        o = [obs("GET", "/users/v1/{param}", "/users/v1/{param}", "coringa"),
             obs("GET", "/users/v1/admin")]
        r = compute_diff(d, o)
        self.assertEqual([(s.method, s.path) for s in r.shadow], [("GET", "/users/v1/{param}")])
        self.assertEqual(r.ambiguos[0].ambiguo_com, "/users/v1/{param}")

    def test_metodo_diferente_nao_agrupa(self):
        o = [obs("GET", "/x/{param}", "/x/{param}", "coringa"), obs("DELETE", "/x/admin")]
        r = compute_diff(set(), o)
        self.assertEqual(len(r.shadow), 2)
