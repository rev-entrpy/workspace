#!/usr/bin/env python3
# Copyright 2026 The Binius Developers
"""Writes docs/diagrams/design.excalidraw: the design of the chain proofs, as one Excalidraw scene.

Run from anywhere:  python3 docs/diagrams/design_diagram.py
Open the output at https://excalidraw.com (menu: Open) or in the Excalidraw VS Code extension.

The scene is drawn in black on white and saved with the dark theme, so it shows white on dark
like the Binius64 constraint-system sketch. Everything is placed by hand below, one section at a
time; the helpers only know how to draw a box, a table, a circle, a line of text and an arrow.
"""

import json
import random
from pathlib import Path

OUT = Path(__file__).with_name("design.excalidraw")

INK = "#1e1e1e"
BLUE = "#1971c2"
RED = "#e03131"
GREEN = "#2f9e44"
VIOLET = "#9c36b5"
ORANGE = "#e8590c"

elements = []
rng = random.Random(7)


def _base(kind, x, y, w, h, color=INK, dashed=False, width=1):
	return {
		"id": f"{kind}-{len(elements)}",
		"type": kind,
		"x": x,
		"y": y,
		"width": w,
		"height": h,
		"angle": 0,
		"strokeColor": color,
		"backgroundColor": "transparent",
		"fillStyle": "solid",
		"strokeWidth": width,
		"strokeStyle": "dashed" if dashed else "solid",
		"roughness": 1,
		"opacity": 100,
		"groupIds": [],
		"frameId": None,
		"roundness": None,
		"seed": rng.randrange(1, 2**31),
		"version": 1,
		"versionNonce": rng.randrange(1, 2**31),
		"isDeleted": False,
		"boundElements": None,
		"updated": 1,
		"link": None,
		"locked": False,
	}


def text(x, y, s, size=16, color=INK, align="left"):
	"""Free text; `x` is the left edge (or the centre, with align="center")."""
	lines = s.split("\n")
	w = max(len(line) for line in lines) * size * 0.55
	h = len(lines) * size * 1.25
	if align == "center":
		x -= w / 2
	e = _base("text", x, y, w, h, color)
	e.update(
		text=s,
		originalText=s,
		fontSize=size,
		fontFamily=1,
		textAlign=align,
		verticalAlign="top",
		containerId=None,
		autoResize=True,
		lineHeight=1.25,
	)
	elements.append(e)
	return e


def rect(x, y, w, h, color=INK, dashed=False, width=1):
	e = _base("rectangle", x, y, w, h, color, dashed, width)
	elements.append(e)
	return e


def box(x, y, w, h, label, size=16, color=INK, dashed=False):
	"""A rectangle with a centred label (free text, so it never re-wraps)."""
	rect(x, y, w, h, color, dashed)
	lines = label.split("\n")
	th = len(lines) * size * 1.25
	text(x + w / 2, y + (h - th) / 2, label, size, color, align="center")


def circle(cx, cy, r, label, size=15, color=INK):
	elements.append(_base("ellipse", cx - r, cy - r, 2 * r, 2 * r, color))
	lines = label.split("\n")
	text(cx, cy - len(lines) * size * 1.25 / 2, label, size, color, align="center")


def arrow(x1, y1, x2, y2, color=INK, dashed=False, label=None, size=14, head=True):
	e = _base("arrow", x1, y1, abs(x2 - x1), abs(y2 - y1), color, dashed)
	e.update(
		points=[[0, 0], [x2 - x1, y2 - y1]],
		lastCommittedPoint=None,
		startBinding=None,
		endBinding=None,
		startArrowhead=None,
		endArrowhead="arrow" if head else None,
		elbowed=False,
		roundness={"type": 2},
	)
	elements.append(e)
	if label:
		text((x1 + x2) / 2, (y1 + y2) / 2 - size * 1.6, label, size, color, align="center")


def table(x, y, title, rows, widths, row_h=28, size=15, color=INK, title_size=20):
	"""Stacked cells, like the Constants / In/Out / Private columns of the sketch.

	`rows` holds one tuple of cell texts per row; `widths` one width per column.
	Returns the y just below the table.
	"""
	if title:
		text(x + sum(widths) / 2, y - title_size * 1.6, title, title_size, color, align="center")
	for i, row in enumerate(rows):
		cx = x
		for cell, w in zip(row, widths):
			box(cx, y + i * row_h, w, row_h, cell, size, color)
			cx += w
	return y + len(rows) * row_h


def section(y, title):
	text(40, y, title, 30)


# --- Title ------------------------------------------------------------------------------------

text(40, 10, "Bitcoin chain proofs on Binius64: the design", 40)
text(
	40,
	64,
	"One proof of fixed size that the chain from genesis to an epoch boundary is valid, extended one epoch at a "
	"time.  Branch v2-folding;  docs/recursion/04-folding.md",
	18,
)

# --- 1. What is proved ------------------------------------------------------------------------

section(120, "1.  What is proved, and what a light client checks")

state_rows = [
	("tip hash [0]",),
	("tip hash [1]",),
	("tip hash [2]",),
	("tip hash [3]",),
	("height",),
	("time",),
	("bits  (nBits)",),
	("epoch start time",),
	("timestamp [0]",),
	("timestamp [1]",),
	("...",),
	("timestamp [10]",),
]
bottom = table(60, 220, "Chain state σ  (19 words)", state_rows, [230])
text(
	60,
	bottom + 10,
	"the tip hash takes 4 words of 64 bits;\nthe other 15 words hold 32-bit values;\n"
	"the 11 timestamps are the median-\ntime-past window  (MtpState)",
	14,
)

# The chain, left to right.
y0 = 250
circle(470, y0 + 45, 62, "genesis\nσ₀", 16)
arrow(532, y0 + 45, 600, y0 + 45)
box(600, y0, 240, 90, "π₀  epoch-0 proof\nmedian-time-past circuit\nheights 0 → 2016   446 KiB", 15, BLUE)
arrow(840, y0 + 45, 900, y0 + 45)
circle(975, y0 + 45, 75, "σ_start\n= σ₂₀₁₆", 16)
arrow(1050, y0 + 45, 1110, y0 + 45)
box(1110, y0, 330, 90, "πₖ  chain proof\nstep circuit S, one step per epoch\n526 KiB at any height", 15, VIOLET)
arrow(1440, y0 + 45, 1500, y0 + 45)
circle(1590, y0 + 45, 90, "σ_tip\n= σ at height\n2016·(k+1)", 15)
arrow(1680, y0 + 45, 1740, y0 + 45)
box(1740, y0, 250, 90, "tail headers\nfewer than 2016\nchecked natively", 15, GREEN)
arrow(1990, y0 + 45, 2050, y0 + 45)
circle(2110, y0 + 45, 55, "tip", 18)

# Inside the chain proof: one step per epoch.
text(1110, y0 + 110, "inside πₖ (by induction):", 15, VIOLET)
for i, lab in enumerate(["epoch 1", "epoch 2", "...", "epoch k"]):
	box(1110 + i * 95, y0 + 140, 75, 40, lab, 14, VIOLET)
	if i:
		arrow(1110 + i * 95 - 20, y0 + 160, 1110 + i * 95, y0 + 160, VIOLET)
text(1110, y0 + 190, "each step verifies the previous step's\nproof inside the circuit, then adds an epoch", 14, VIOLET)

text(
	600,
	y0 + 260,
	"Light client  (ChainVerifier::verify)\n"
	"1. verify π₀ from genesis; its after-state must equal σ_start\n"
	"2. verify πₖ against S's constraint system\n"
	"3. decider: check the accumulated claim  T̃_S(p_acc) = v_acc  (one pass, ~1.3 s)\n"
	"4. advance σ_tip over the tail headers with the native rules R1–R5\n"
	"   → the tip state.  Steps 1–3 cost the same at every height.",
	16,
)
text(
	1500,
	y0 + 260,
	"Prover  (ChainProver)\n"
	"first(σ_start, epoch 1)  → π₁\n"
	"extend(πₖ₋₁, epoch k)  → πₖ\n"
	"one epoch (2016 headers) per step, about 45 s;\n"
	"a full node adds a step every two weeks",
	16,
)

table(
	2280,
	220,
	"v1-main vs v2-folding",
	[
		("", "certificate", "chain proof"),
		("proofs", "1 per epoch", "2 (π₀ and πₖ)"),
		("size", "+446 KiB / epoch", "972 KiB total"),
		("check", "~30 ms / epoch", "~1.3 s, constant"),
		("prove", "0.2–0.4 s / epoch", "~45 s / epoch"),
	],
	[120, 190, 190],
	row_h=34,
)

# --- 2. The step circuit S --------------------------------------------------------------------

sy = 720
section(sy, "2.  The step circuit S  (one fixed circuit; a proof of S is πₖ)")
rect(40, sy + 50, 3320, 840, dashed=True)

# Public and private columns.
pub_bottom = table(
	80,
	sy + 140,
	"Public statement (182 words)",
	[
		("σ_start", "19"),
		("σ_tip", "19"),
		("acc: point p  (71 elements)", "142"),
		("acc: value v", "2"),
	],
	[270, 60],
	row_h=40,
	color=BLUE,
)
text(
	80,
	pub_bottom + 12,
	"claim elements take 2 words each, low half first.\n"
	"σ_start feeds the joins; σ_tip and acc are\nbound to the outputs on the right.",
	14,
	BLUE,
)
priv_bottom = table(
	80,
	pub_bottom + 150,
	"Private witness",
	[
		("active  (all ones, or 0 on step 1)",),
		("epoch number e",),
		("2016 headers × 80 bytes",),
		("previous proof πₖ₋₁ (replayed)",),
		("fold transcript (replayed)",),
	],
	[330],
	row_h=36,
	color=RED,
)

# The inner verifier.
vx, vy, vw, vh = 480, sy + 110, 700, 570
rect(vx, vy, vw, vh, VIOLET, width=2)
text(vx + 16, vy + 12, "Inner verifier: a proof of S itself", 22, VIOLET)
text(
	vx + 16,
	vy + 52,
	"reads the previous statement\n"
	"  [ σ_start' | σ_prev | acc_prev ]   (182 words, as wires)\n\n"
	"① witness commitment  (Merkle root)\n"
	"② AND / MUL constraint sumchecks\n"
	"③ shift reduction  →  wiring claim, deferred\n"
	"④ BaseFold / FRI opening: folds, Merkle paths\n"
	"⑤ grinding nonce\n\n"
	"every assertion here is conditional on active\n"
	"    builder.set_assert_condition(Some(active))\n"
	"algebraic folding is off while it is recorded\n"
	"    builder.set_algebraic_folding(false)\n\n"
	"the proof's bytes become input wires, filled by replaying\n"
	"the proof (WitnessFillerChannel); Fiat–Shamir challenges\n"
	"are recomputed in the circuit with SHA-256.\n"
	"About 7.3 M of S's 12.3 M constraints.",
	16,
)
flow = ["statement", "① commit", "② sumchecks", "③ shift\nreduction", "④ opening", "⑤ grind"]
for i, lab in enumerate(flow):
	bx0 = vx + 16 + i * 113
	box(bx0, vy + 480, 95, 56, lab, 13, VIOLET)
	if i:
		arrow(bx0 - 18, vy + 508, bx0, vy + 508, VIOLET)

# Outputs of the inner verifier, and the joins.
ox = vx + vw
circle(1375, vy + 60, 44, "=  if\nactive", 14)
circle(1375, vy + 210, 44, "select\nby active", 14)
circle(1375, vy + 470, 44, "select\nby active", 14)
arrow(ox, vy + 60, 1331, vy + 60, label="σ_start'")
arrow(ox, vy + 210, 1331, vy + 210, label="σ_prev")
arrow(ox, vy + 360, 1290, vy + 360, head=False)
text(ox + 40, vy + 334, "acc_prev", 14)
arrow(1290, vy + 360, 1345, vy + 438)
arrow(1290, vy + 360, 1500, vy + 420, dashed=True)
text(1400, vy + 356, "acc_prev", 13)
arrow(ox, vy + 550, 1345, vy + 502, label="c = (p_c, v_c)")
box(1250, vy + 118, 90, 36, "σ_start", 14, BLUE)
arrow(1310, vy + 118, 1350, vy + 96, BLUE)
arrow(1310, vy + 154, 1350, vy + 176, BLUE)
text(1318, vy + 258, "active ? σ_prev\n       : σ_start", 13)
text(1318, vy + 518, "active ? c\n       : acc_prev", 13)
arrow(1419, vy + 210, 1500, vy + 210, label="before")
arrow(1419, vy + 470, 1500, vy + 470, label="chosen")

# The epoch rules.
ex, ey, ew, eh = 1500, vy, 800, 360
rect(ex, ey, ew, eh, GREEN, width=2)
text(ex + 16, ey + 12, "Epoch rules  (EpochWires::define_on)", 22, GREEN)
text(
	ex + 16,
	ey + 50,
	"before → 2016 headers → σ_tip\n"
	"heights: before = 2016·e = (e≪11) − (e≪5),  1 ≤ e < 2²¹;  after = before + 2016\n"
	"for each header h = 1 … 2016:\n"
	"   R1  its prev-hash field is the hash of header h−1\n"
	"   R2  nBits encodes a valid target\n"
	"   R3  double-SHA-256(header) ≤ target   (proof of work)\n"
	"   R4  nBits = the required bits; the last header retargets\n"
	"   R5  time > median of the previous 11 timestamps\n"
	"the constraints of v1-main's epoch circuit, about 2.4 M",
	15,
)
hy = ey + 270
box(ex + 16, hy, 130, 60, "header h\n80 bytes", 14, GREEN)
arrow(ex + 146, hy + 30, ex + 190, hy + 30, GREEN)
circle(ex + 235, hy + 30, 44, "SHA-256", 13, GREEN)
arrow(ex + 279, hy + 30, ex + 320, hy + 30, GREEN)
circle(ex + 365, hy + 30, 44, "SHA-256", 13, GREEN)
arrow(ex + 409, hy + 30, ex + 450, hy + 30, GREEN)
circle(ex + 485, hy + 30, 34, "≤", 20, GREEN)
arrow(ex + 590, hy + 30, ex + 520, hy + 30, GREEN)
box(ex + 590, hy, 190, 60, "target from nBits\n(R2, R4)", 14, GREEN)
arrow(ex + ew, ey + 60, ex + ew + 120, ey + 60, BLUE, label="σ_tip (public)")

# The fold verifier.
fx, fy, fw, fh = 1500, vy + 400, 800, 280
rect(fx, fy, fw, fh, ORANGE, width=2)
text(fx + 16, fy + 12, "Fold verifier  (sibling channel, fresh Fiat–Shamir)", 22, ORANGE)
text(
	fx + 16,
	fy + 50,
	"recv acc_prev and chosen as messages; assert they equal the wires\n"
	"   (so both claims enter the hash before any challenge)\n"
	"α ← batching challenge\n"
	"71 sumcheck rounds, degree 2, over  Σₓ T(x)·[eq(p₁,x) + α·eq(p₂,x)]\n"
	"recv v' = T̃(r);   check  v'·[eq(p₁,r) + α·eq(p₂,r)] = the last round's value\n"
	"acc = (r, v')   → bind_public_elems\n"
	"a few thousand constraints",
	15,
)
arrow(fx + fw, fy + 140, fx + fw + 120, fy + 140, BLUE, label="acc (public)")

# Soundness notes on the right.
text(
	2450,
	sy + 110,
	"Why a proof of S means the whole chain is valid\n\n"
	"πₖ verifies  ⇒  a proof πₖ₋₁ of S exists for\n"
	"[σ_start | σ_prev | acc_prev], one epoch takes\n"
	"σ_prev to σ_tip, and acc folds acc_prev with\n"
	"πₖ₋₁'s claim c.  By induction every epoch from\n"
	"σ_start is valid, provided acc holds: it has\n"
	"absorbed every claim of the chain.\n\n"
	"First step (active = 0)\n"
	"the verifier's checks are off; before = σ_start;\n"
	"the witness replays an all-zero dummy proof;\n"
	"acc₀ = a true claim, T̃_S at the zero point;\n"
	"fold(acc₀, acc₀) is still true.\n"
	"Switching off mid-chain gains nothing: the proof\n"
	"then only covers one epoch from σ_start.\n\n"
	"S at its fixed point\n"
	"12,303,358 constraints:\n"
	"   2,256,844 zero · 8,203,314 AND\n"
	"   1,843,200 binary-field MUL\n"
	"2,407 constants · 182 public words",
	16,
)

# --- 3. What a proof leaves unchecked, and the fold ---------------------------------------------

ty = 1660
section(ty, "3.  What a proof leaves unchecked, and how it is folded")

# 3a. A proof, as a flow.
text(60, ty + 60, "What a Binius64 proof checks", 20)
steps3 = [
	("witness words:  Constants | In/Out | Private", INK),
	("① Merkle commitment of the encoded words", INK),
	("② AND / MUL constraint sumchecks\n→ claims about the constraints' operands", INK),
	("③ shift reduction: an operand is an XOR of shifted words", INK),
]
y = ty + 100
for i, (lab, color) in enumerate(steps3):
	box(60, y, 460, 56, lab, 15, color)
	if i + 1 < len(steps3):
		arrow(290, y + 56, 290, y + 84)
	y += 84
arrow(200, y - 28, 150, y + 30)
arrow(380, y - 28, 480, y + 30)
box(40, y + 30, 300, 110, "witness claim\n→ ④ BaseFold / FRI opening\n+ ⑤ grinding nonce\nchecked by the verifier", 15, GREEN)
box(360, y + 30, 330, 110, "wiring claim  W_CS(r) = v\ncosts a pass over every term\nof every constraint\n→ deferred  (DeferredWiringClaim)", 15, RED)
text(
	40,
	y + 160,
	"All challenges come from hashing the transcript (Fiat–Shamir).\n"
	"A proof is 434–526 KiB, mostly Merkle openings. The wiring claim\n"
	"is the only linear-cost check: done inside S it would make S\n"
	"bigger than itself, so S outputs (r, v) instead and folds it.",
	15,
)

# 3b. The tensor's index layout, one cell per bit, and one term becoming one nonzero.
bx, by, bit = 800, ty + 130, 14
axes = [
	("op", 2, INK),
	("constraint  r_x", 24, BLUE),
	("operand", 3, INK),
	("inner shift", 8, GREEN),
	("outer shift", 8, GREEN),
	("value  r_y + 1", 26, RED),
]
text(bx, ty + 60, "The wiring tensor T_S: one index = 71 bits, lowest first", 20)
cx = bx
for name, bits, color in axes:
	box(cx, by, bits * bit, 44, str(bits), 14, color)
	text(cx + bits * bit / 2, by + 52, name, 13, color, align="center")
	cx += bits * bit
text(
	bx,
	by + 90,
	"One nonzero (value 1) per operand term; terms at the same index add.\n"
	"S has 135,524,598 nonzeros  (WiringTensor::new).\n"
	"A wiring claim is  T̃_S(p) = v:  a point p of 71 elements and a value v.\n"
	"The verifier's claim inputs are [λ | operand | r_x | rest]; tensor_point moves r_x\n"
	"in front. The four operations stack on the op axis: the verifier's eq(λ, op)-\n"
	"weighted sum over them is one evaluation of the stacked tensor.",
	15,
)

# One term, in the style of the constraint-system sketch.
ty2 = by + 280
text(bx, ty2 - 30, "One term → one nonzero", 18)
table(bx, ty2 + 30, "Constants", [("0x00…00",), ("0xFF…FF",), ("…",)], [130], row_h=26, size=13, title_size=15)
table(bx + 150, ty2 + 30, "In/Out", [("σ_start",), ("σ_tip",), ("acc",)], [120], row_h=26, size=13, title_size=15)
table(
	bx + 290,
	ty2 + 30,
	"Private",
	[("w₀",), ("…",), ("w₁₇",), ("…",), ("w₄₀",), ("…",)],
	[110],
	row_h=26,
	size=13,
	title_size=15,
)
circle(bx + 490, ty2 + 60, 26, "≪7", 14)
circle(bx + 580, ty2 + 110, 32, "XOR", 14)
arrow(bx + 400, ty2 + 95, bx + 464, ty2 + 66)
arrow(bx + 516, ty2 + 70, bx + 552, ty2 + 96)
arrow(bx + 400, ty2 + 147, bx + 548, ty2 + 118)
box(bx + 660, ty2 + 80, 110, 60, "operand A", 14, BLUE)
arrow(bx + 612, ty2 + 110, bx + 660, ty2 + 110)
text(bx + 780, ty2 + 92, "&  B  =  C", 18)
text(bx + 660, ty2 + 150, "AND constraint i", 14, BLUE)
text(
	bx,
	ty2 + 210,
	"the term (w₁₇ ≪ 7) in operand A of AND constraint i is the nonzero at\n"
	"[ op AND | constraint i | operand A, inner shift ≪7 | outer shift none | address of w₁₇ ];\n"
	"w₄₀ (no shift) is a second nonzero in the same operand.",
	15,
)

# 3c. The fold.
gx = 2200
text(gx, ty + 60, "Folding two claims  (fold.rs, upstream batch_eval)", 20)
circle(gx + 90, ty + 190, 80, "T̃(p₁) = v₁\nacc_prev", 15)
circle(gx + 90, ty + 380, 80, "T̃(p₂) = v₂\nchosen", 15)
arrow(gx + 170, ty + 200, gx + 300, ty + 270)
arrow(gx + 170, ty + 370, gx + 300, ty + 300)
circle(gx + 355, ty + 285, 55, "fold\n71 rounds", 15, ORANGE)
arrow(gx + 410, ty + 285, gx + 520, ty + 285)
circle(gx + 610, ty + 285, 88, "T̃(r) = v'\nacc", 16)
text(
	gx,
	ty + 490,
	"1. α ← challenge\n"
	"2. claim  Σₓ T(x)·[eq(p₁,x) + α·eq(p₂,x)] = v₁ + α·v₂\n"
	"3. 71 rounds: the prover sends a degree-2 polynomial,\n"
	"   the verifier checks it and answers with a challenge\n"
	"4. the rounds end at a random point r\n"
	"5. the prover sends v' = T̃(r)\n"
	"6. the verifier checks v'·[eq(p₁,r) + α·eq(p₂,r)]\n"
	"   against the last round's value\n\n"
	"If either claim is false, the folded claim is false\n"
	"except with probability ≈ (1 + 3·71)/2¹²⁸, so a false\n"
	"claim anywhere reaches the light client's decider.\n"
	"Prover: claim_fold::prove, a sparse sumcheck over T_S's\n"
	"nonzeros; indices are u128 (T_S has 71 index bits).",
	15,
)

# --- 4. One step, and the fixed point ---------------------------------------------------------

py = 2520
section(py, "4.  Proving one step, and finding S")

steps = [
	("πₖ₋₁\n526 KiB", None, VIOLET),
	("replay πₖ₋₁\nthrough the in-circuit\nverifier (fills its\nwires, yields c)", "0.0–0.9 s", INK),
	("fill the epoch's\n2016 headers", "~0 s", GREEN),
	("WiringTensor::new\n135.5 M nonzeros\n4.3 GB", "2–3 s", RED),
	("fold::prove\n71 sparse sumcheck\nrounds", "42–49 s", ORANGE),
	("replay the fold\ntranscript through\nthe fold verifier", "~0 s", ORANGE),
	("populate the\nwitness", "0.2 s", INK),
	("prove S\n12.3 M constraints", "~1 s", INK),
	("πₖ\n526 KiB", None, VIOLET),
]
x = 60
for i, (label, t, color) in enumerate(steps):
	w = 150 if t is None else 230
	box(x, py + 80, w, 110, label, 15, color)
	if t:
		text(x + w / 2, py + 200, t, 16, color, align="center")
	if i + 1 < len(steps):
		arrow(x + w, py + 135, x + w + 40, py + 135)
	x += w + 40
text(
	60,
	py + 240,
	"ChainProver::extend: one epoch per step, 45–52 s in total on an M1 Pro with 16 GB; the fold is almost all of it.",
	16,
)

# The fixed point.
fy2 = py + 300
text(60, fy2, "The fixed point  (StepCircuit::fixed_point)", 22)
text(
	60,
	fy2 + 36,
	"S contains a verifier for S, so S is rebuilt around its own verifier until a build reproduces, "
	"byte for byte, the system it verified.",
	16,
)
chain = [
	("epoch circuit\n(seed)", ""),
	("S₁", "11.24 M\n176 words"),
	("S₂", "12.30 M\n182 words"),
	("S₃", ""),
	("S₄", "12,303,358\n2,407 constants"),
	("S₅ = S₄", "fixed point"),
]
x = 60
for i, (label, note) in enumerate(chain):
	box(x, fy2 + 90, 170, 70, label, 16, INK if i < 5 else GREEN)
	if note:
		text(x + 85, fy2 + 170, note, 14, align="center")
	if i + 1 < len(chain):
		arrow(x + 170, fy2 + 125, x + 280, fy2 + 125, label="build(V(·))", size=13)
	x += 280
text(
	1760,
	fy2 + 80,
	"First searches never settled: from S₄ on every constraint was equal, but each build had\n"
	"195 more constants. The verifier folds the inner circuit's constants with its statement;\n"
	"the builder's algebraic folding turned XORs of two constant wires into new constants,\n"
	"which the next build then verified.  Fix: set_algebraic_folding(false) around the inner\n"
	"verifier, so such an XOR stays a linear term (free in Binius64). About 40 s per build;\n"
	"the example saves S to target/step-circuit.bin and later runs confirm it in one build.",
	15,
)

# --- 5. Code map and measurements ------------------------------------------------------------

cy = 3090
section(cy, "5.  Where the code is")


def crate(x, y, w, h, title, body, color):
	rect(x, y, w, h, color, width=2)
	text(x + 14, y + 10, title, 20, color)
	text(x + 14, y + 44, body, 14)


crate(
	60,
	cy + 60,
	500,
	200,
	"bitcoin-native",
	"The rules in plain Rust.\n"
	"Header, hashes, targets, retarget arithmetic\n"
	"MtpState (σ), MtpStatement (before, after)\n"
	"advance(σ, headers): rules R1–R5 natively\n"
	"tests/fixtures: headers-0-4100, headers-4101-6100",
	GREEN,
)
crate(
	640,
	cy + 60,
	560,
	200,
	"bitcoin-sync",
	"The circuits and their provers.\n"
	"circuit/mtp.rs: constrain_state, apply_headers\n"
	"circuit/epoch.rs: EpochWires::define, define_on\n"
	"mtp.rs, epoch.rs: fill_witness, provers, verifiers\n"
	"state_words(σ): the 19 statement words\n"
	"fingerprint tests pin every circuit (28)",
	GREEN,
)
crate(
	1280,
	cy + 60,
	760,
	220,
	"bitcoin-recursion",
	"Composing proofs.\n"
	"proof.rs — setup, prove, verify, verify_deferred (returns the wiring claim)\n"
	"wiring.rs — WiringTensor (entries, evaluate), tensor_point\n"
	"fold.rs — Claim, fold::prove (native), fold::verify (any channel)\n"
	"chain.rs — StepCircuit (build, fixed_point, witness), ChainProof,\n"
	"      ChainProver (first, extend), ChainVerifier (the light client)\n"
	"certificate.rs, headers_file.rs — segment certificates (v1)\n"
	"examples: chain, certificate, fetch_headers, two_segments\n"
	"tests: wiring (tensor, fold), chain (slow, #[ignore]), certificate",
	VIOLET,
)
crate(
	2120,
	cy + 60,
	640,
	220,
	"Binius64 (upstream) additions",
	"frontend — CircuitBuilder::set_assert_condition,\n"
	"      CircuitBuilder::set_algebraic_folding\n"
	"ip-prover — u128 sparse indices; FactoredMultilinear::get_pair;\n"
	"      claim_fold::prove takes its entries by value\n"
	"verifier — WiringEvalShape::inout, section_lens\n"
	"recursion — Binius64BuilderChannel::builder, sibling,\n"
	"      input_count; elem made public\n"
	"used as they are: batch_eval (the fold verifier), claim_fold,\n"
	"      WitnessFillerChannel, DeferredWiringClaim",
	RED,
)
arrow(560, cy + 160, 640, cy + 160)
arrow(1200, cy + 160, 1280, cy + 160)
arrow(2120, cy + 195, 2040, cy + 195)

table(
	60,
	cy + 420,
	"Measured  (mainnet 0–16,000, epochs 1–6, M1 Pro 16 GB)",
	[
		("epoch-0 proof", "7.7 s"),
		("S: one confirming build", "49 s"),
		("prover setup", "3.3 s"),
		("one step (fold ~45 s, prove ~1 s)", "44.6–47.4 s"),
		("chain proof", "526 KiB"),
		("light-client setup", "10.1 s"),
		("light-client check", "1.31 s"),
		("peak memory", "8.9 GB resident"),
	],
	[360, 170],
	row_h=32,
)
text(
	700,
	cy + 400,
	"Open\n"
	"· the fold: ~45 s and 4.3 GB per step (merge entries late, share one read per round)\n"
	"· memory: S's build and the fold each need several GB; 16 GB swaps\n"
	"· light-client setup: load S from a file and check its hash instead of building it\n"
	"· chainwork: not in the statement yet\n"
	"· demo to 40,319: headers past 16,000 still to fetch",
	16,
)

scene = {
	"type": "excalidraw",
	"version": 2,
	"source": "https://excalidraw.com",
	"elements": elements,
	"appState": {"viewBackgroundColor": "#ffffff", "theme": "dark", "gridSize": None},
	"files": {},
}
OUT.write_text(json.dumps(scene, indent=1, ensure_ascii=False) + "\n")
print(f"wrote {OUT} ({len(elements)} elements)")

