"""Sanity tests for the four attack modules."""
import random

from src.attacks.direct_injector import DirectInjector
from src.attacks.encoding_obfuscator import EncodingObfuscator
from src.attacks.indirect_embedder import IndirectEmbedder
from src.attacks.multi_turn_eroder import MultiTurnEroder


def test_direct_injector_generates_prompts():
    atks = DirectInjector(rng=random.Random(0)).generate("siem", "log-line", 3)
    assert len(atks) == 3
    for a in atks:
        assert a.module == "direct"
        assert "log-line" in a.prompt
        assert a.injected_instruction


def test_indirect_embedder_places_payload_inside_content():
    atks = IndirectEmbedder(rng=random.Random(0)).generate(
        "threat_report", "CVE-2025-00001 body text", 4
    )
    for a in atks:
        assert a.module == "indirect"
        assert a.injected_instruction in a.prompt


def test_multiturn_eroder_produces_five_turns():
    atks = MultiTurnEroder(rng=random.Random(0)).generate("malware", "sample-report", 2)
    for a in atks:
        assert len(a.turns) == 5
        assert "SYSTEM PROMPT" in a.turns[-1]


def test_encoding_obfuscator_covers_all_schemes():
    schemes = set()
    for _ in range(50):
        atks = EncodingObfuscator(rng=random.Random()).generate("analyst", "q?", 1)
        schemes.add(atks[0].metadata["scheme"])
    assert schemes == {"base64", "rot13", "homoglyph"}
