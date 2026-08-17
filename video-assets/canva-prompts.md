# Canva Animated Diagram Prompts — LF | Observability for AI Agents

**How to use this doc**: each block below is a prompt you paste into Canva AI (or Canva Magic Design). The **STYLE BLOCK** below applies to every diagram — paste it at the top of the prompt if Canva loses style continuity. The **ANIMATION notes** describe the order and timing of the animation you'll build in Canva after generating the base image.

---

## STYLE BLOCK (paste at the top of every prompt if needed)

> Flat vector illustration. Clean tech style, no 3D, no photorealism. Color palette: primary accent Strands orange #FF6B35, secondary accent AWS blue #232F3E, tool success green #34A853, backgrounds white #FFFFFF, text dark #1A1A1A, secondary text grey #6B7280. Sans-serif typography (Inter or Helvetica), 16:9 aspect ratio (1920×1080). Rounded rectangles with soft shadows for boxes. Grey #9CA3AF elbow lines for connectors. Minimalist, no clutter.

---

## Section 1 — Hook (0:00–0:45)

### Diagram 1.1 — Server monitoring dashboard (traditional observability)

**Purpose**: Contraste visual con la observabilidad agéntica. Muestra "lo viejo".

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> A traditional server monitoring dashboard in the style of Grafana or Datadog. 16:9. Four gauge widgets arranged in a 2×2 grid: CPU 12% (green semicircle gauge), RAM 40% (green semicircle gauge), Disk 65% (green gauge), Uptime 99.99% (large solid green tile with the number). Below the gauges, a flat horizontal line graph showing a boring healthy CPU trend across 24 hours. Muted grey background #F5F5F5. Use soft greens and greys ONLY — no orange or blue accents. This should feel intentionally "old / boring / traditional" to contrast with agent observability. No AI-related terms, no agent icons.

**Animation notes**:
- Fade in on 0:08.
- Gauges pulse gently (a subtle "everything is fine" heartbeat) for 3 seconds.
- Fade out on 0:11, back to Eli.

---

### Diagram 1.2 — Three pillars of agent observability

**Purpose**: Los 3 puntos que Eli enumera. Se revelan uno a uno.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> Three vertically stacked cards on a white background, 16:9. Each card is a rounded rectangle with a small icon on the left and a bold label on the right. Card 1 (top): wrench/gear icon in Strands orange #FF6B35, label "Which tool the model chose". Card 2 (middle): a circular refresh/loop icon in Strands orange, label "How many reasoning cycles". Card 3 (bottom): a dollar sign icon in AWS blue #232F3E, label "How many tokens (= efficiency)". 24px vertical spacing between cards, subtle drop shadows. Dark text #1A1A1A. Sans-serif typography. No servers, no CPU gauges — this is the opposite of the previous dashboard.

**Animation notes**:
- Card 1 slides in from the right on 0:22.
- Card 2 slides in on 0:25.
- Card 3 slides in on 0:28.
- All 3 remain visible until 0:30, then fade.

---

### Diagram 1.3 — Strands → AgentCore promise

**Purpose**: Cierre del hook — dónde vamos.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> Two large rounded-rectangle badges side by side, connected by a right-pointing arrow. 16:9. White background. Left badge: labeled "Strands Agents" with a bold "S" mark in Strands orange #FF6B35 and subtitle "Build the observability". Right badge: labeled "Amazon Bedrock AgentCore" with the AWS orange smile hint and subtitle "Take it to production". Between the badges, a grey #6B7280 arrow with a small annotation floating above it: "practically zero config". Minimalist, professional tech style, no clutter.

**Animation notes**:
- Left badge fades in on 0:38.
- Arrow draws itself left-to-right on 0:40.
- Right badge fades in on 0:42.
- "practically zero config" annotation types out or fades in on 0:43.

---

## Section 2 — Layer 1: Metrics (0:45–3:15)

### Diagram 2.1 — Layer 1 card (the pillar that stays visible)

**Purpose**: Card acumulativa que se queda en la esquina toda la sección. Se va llenando con las 4 subcapas.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> A single rounded rectangle card centered on a white 16:9 frame (1920×1080). The card itself is portrait-proportioned (approx 400×600 px) and floats in the center of the horizontal canvas with generous white space on both sides. White card background with subtle drop shadow. Header: bold text "Layer 1" on top, larger bold "Metrics" below it. A horizontal divider line. Below the divider, four sub-labels stacked vertically, each with a small circular status indicator on the left (empty circle = pending, filled circle in Strands orange #FF6B35 = active). Sub-labels: "1. Reasoning cycles", "2. Tool metrics", "3. Model metrics", "4. Per-request + aggregate". All indicators start empty (grey outline). Dark text, sans-serif, generous padding.

**Animation notes**:
- Card slides into the top-right corner on 1:00 and stays visible.
- Sub-label 1 indicator fills orange when Eli reaches Concept 1 (~1:00).
- Sub-label 2 fills at ~1:35.
- Sub-label 3 fills at ~2:10.
- Sub-label 4 fills at ~2:45.
- At 3:15, the whole card fades out (transitions to Layer 2).

---

### Diagram 2.2 — Reasoning cycles loop

**Purpose**: Animación del loop del agente — el agente NO es una llamada, es un ciclo.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> A circular flow diagram in the center of a white 16:9 frame. In the middle, a brain/thought icon (grey #6B7280). Around it, a large circular arrow going clockwise, drawn in Strands orange #FF6B35, thick stroke, with an arrowhead. On the arrow's path, three small nodes evenly spaced: node 1 labeled "Cycle 1", node 2 labeled "Cycle 2", node 3 labeled "Cycle 3", each a small circle with the label below. Bottom of the frame, a counter that reads "3 reasoning cycles" in bold dark text. Minimalist, clean, no other elements.

**Animation notes**:
- Brain icon appears on 1:10.
- Circular arrow draws itself, going around once. On each pass it stops briefly at each cycle node, which pulses orange and increments the counter (1 → 2 → 3). Total ~5 seconds.
- Freeze on final state "3 reasoning cycles" through 1:35.

---

### Diagram 2.3 — Tool metrics breakdown

**Purpose**: Muestra las 3 tools con sus 3 métricas por tool.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> Three horizontal cards stacked vertically on a white background, 16:9. Each card represents one tool. Card 1: airplane icon (Strands orange), label "search_flights", and three small stat badges below the label: "called: 1", "time: ~600 ms", "status: success" (success in green #34A853). Card 2: sun/cloud icon, label "get_weather", stats "called: 1", "time: 1.4 s", "status: success". Card 3: database icon, label "book_flight", stats "called: 1", "time: instant", "status: success". Right side of each card, a mini bar-chart-style visualization comparing the timings — search_flights and get_weather have visible bars, book_flight is nearly flat. Clean flat-vector style.

**Animation notes**:
- Card 1 slides in from the left on 1:45 with its stats revealed one by one (called → time → status).
- Card 2 slides in on 1:55.
- Card 3 slides in on 2:03.
- Mini timing bar chart on the right fills in as each card lands.

---

### Diagram 2.4 — Model metrics (tokens + latency)

**Purpose**: Los dos números del modelo: tokens (input/output/total) y latency.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> Center of the 16:9 frame: a large stylized LLM icon (a labeled rectangle or brain-with-circuit-lines) in AWS blue #232F3E. Left of the icon, an input arrow pointing right with the label "Input tokens: 2,523". Right of the icon, an output arrow pointing right with the label "Output tokens: 222". Below the icon, a large bold number "2,745 tokens total" in AWS blue. Bottom-right corner, a stopwatch icon in grey with the label "Model latency: measured per call". Minimalist, no clutter.

**Animation notes**:
- LLM icon appears on 2:15.
- Input arrow draws itself and the token count types in on 2:20.
- Output arrow draws itself and its token count types in on 2:28.
- Total number "2,745 tokens total" fades in on 2:35.
- Stopwatch and latency label fade in on 2:40.

---

### Diagram 2.5 — Per-request vs Aggregate (split screen)

**Purpose**: La misma métrica, dos niveles.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> Split-screen composition, 16:9. Vertical divider down the middle. LEFT half labeled "Per request" (bold, top): a single small trace-like card showing a query icon, "cycles: 3", "tokens: 2,745", "time: 6.3s". RIGHT half labeled "Aggregate" (bold, top): a wide dashboard-like widget with a line chart showing many runs over time (blurred/generalized), a large number "12,847 requests this week", and small stat tiles for "avg cycles: 3.2", "avg tokens: 2,801", "p95 latency: 5.4s". Left side feels intimate/single; right side feels sprawling/many. Use Strands orange as accent on the left, AWS blue on the right.

**Animation notes**:
- Left half fades in on 2:47.
- Right half fades in on 2:55.
- A small caption at the bottom types in on 3:00: "Debug the one, monitor the many."

---

## Section 3 — Layer 2: Traces (3:15–5:30)

### Diagram 3.1 — Layer 2 card (accumulating stack)

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> Two stacked pillar cards in the top-right corner of a white 16:9 frame. Bottom card (already visible, dimmed 60%): "Layer 1 — Metrics" with all four sub-labels showing filled orange indicators. Top card (freshly landed): "Layer 2 — Traces" with four sub-labels stacked below: "1. Trace & spans", "2. OpenTelemetry standard", "3. Documented hierarchy", "4. Span attributes", all with empty indicators. 24px vertical spacing between the two cards. Both have subtle drop shadows.

**Animation notes**:
- Layer 2 card slides in from above on 3:20 and lands on top of the (dimmed) Layer 1 card.
- Sub-label indicators fill in as Eli reaches each concept (3:35, 4:05, 4:30, 5:05).

---

### Diagram 3.2 — What is a trace? What is a span?

**Purpose**: Definición visual del concepto trace y span.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> Horizontal timeline on a white 16:9 frame. At the top, a long thin bar labeled "1 trace = one full request" in Strands orange #FF6B35. Below it, four smaller stacked bars aligned as a timeline (like a Gantt chart / flame graph), each labeled: "span 1 — think", "span 2 — call tool", "span 3 — think", "span 4 — call another tool". Each span has slight overlap or sequential arrangement to show they happen inside the trace. Below the timeline, a legend: "trace = the whole request, span = one step inside it". Clean flat-vector style, no clutter.

**Animation notes**:
- Trace bar draws itself left-to-right on 3:45.
- Spans appear one by one underneath, in sync with Eli listing "thinks, calls a tool, thinks again, calls another tool" (~3:48–3:55).
- Legend fades in on 4:00.

---

### Diagram 3.3 — OpenTelemetry as the standard

**Purpose**: Muestra que Strands emite OTEL y cualquier backend lo lee.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> Center-left: a rounded rectangle labeled "Strands Agents" in Strands orange, with a smaller "OTEL out" label underneath. From it, a single arrow points right to a hub icon labeled "OpenTelemetry" (industry-standard purple/blue, but you can use grey #6B7280 for neutrality). From the OTEL hub, four arrows radiate out to four labeled endpoints: "Datadog", "Jaeger", "Honeycomb", "Amazon CloudWatch". Each endpoint is a small logo-style badge in a rounded rectangle. Layout: hub-and-spoke. 16:9.

**Animation notes**:
- Strands badge appears on 4:07.
- Arrow to OTEL hub draws on 4:10.
- OTEL hub appears on 4:12.
- Four backend endpoints fade in one by one as Eli names them (4:15–4:25).

---

### Diagram 3.4 — The documented span hierarchy (REAL structure with 3 cycles)

**Purpose**: EL diagrama central de la sección. Muestra la jerarquía real del agente cuando corre.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> A hierarchical tree diagram on a white 16:9 frame. Nodes are rounded rectangles with a bold label and a small subtitle. Connect with grey #9CA3AF elbow lines showing parent-child hierarchy.
>
> Root (Strands orange border): "invoke_agent Strands Agents" / "the whole run"
>
> Three children of the root, indented once (grey border):
> - "execute_event_loop_cycle (1)" / "cycle 1 — parallel tools"
> - "execute_event_loop_cycle (2)" / "cycle 2 — booking"
> - "execute_event_loop_cycle (3)" / "cycle 3 — final answer"
>
> Under cycle (1), indented twice, three children:
> - "chat" / "model call (LLM)" — AWS blue border
> - "execute_tool search_flights" / "Duffel API" — tool green #34A853 border
> - "execute_tool get_weather" / "Open-Meteo" — tool green border
>
> Under cycle (2), indented twice, two children:
> - "chat" / "model call (LLM)" — AWS blue border
> - "execute_tool book_flight" / "SQLite ledger" — tool green border
>
> Under cycle (3), indented twice, one child:
> - "chat" / "model call (LLM)" — AWS blue border
>
> Title above the diagram (bold, dark text): "The agent's decision tree". Subtitle italic grey: "Every span is a decision, every attribute is context."
>
> **See `section-03-span-tree.svg` in this folder for the exact layout — you can import that SVG directly into Canva as a starting point.**

**Animation notes**:
- Root node appears first on 4:33.
- Cycle (1) node slides in from the right on 4:38.
- Its 3 children (chat + search_flights + get_weather) appear together on 4:42, with "parallel" annotation.
- Cycle (2) slides in on 4:48.
- Its 2 children appear on 4:52.
- Cycle (3) slides in on 4:57.
- Its child (chat) appears on 5:00.
- Freeze on the full tree through 5:05.

---

### Diagram 3.5 — Span attributes zoom

**Purpose**: Muestra qué atributos carga cada tipo de span (para el Concepto 4).

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> Two side-by-side "zoomed span" callout cards on a white 16:9 frame. LEFT card: title "chat span", model icon (AWS blue), and a list of key-value attributes below: "gen_ai.request.model: gpt-4o-mini", "gen_ai.usage.input_tokens: ...", "gen_ai.usage.output_tokens: ...", "gen_ai.usage.total_tokens: ...", "prompt: ...", "completion: ...". RIGHT card: title "execute_tool span", tool icon (green), attributes: "gen_ai.tool.name: book_flight", "gen_ai.tool.call.id: ...", "input args: {...}", "tool result: {...}", "gen_ai.tool.status: success". Attributes rendered in monospace font, one per line, key in bold, value in secondary grey. Between the two cards, a small callout: "Every step, fully instrumented."

**Animation notes**:
- Left card fades in on 5:10 with its attributes appearing one by one, quickly.
- Right card fades in on 5:15.
- Central callout appears last on 5:20.

---

## Section 4 — Layer 3: Trace Attributes (5:30–7:30)

### Diagram 4.1 — Layer 3 card (three cards stacked now)

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> Three stacked pillar cards in the top-right corner of a white 16:9 frame. Bottom (dimmed 60%): "Layer 1 — Metrics" with 4 filled indicators. Middle (dimmed 60%): "Layer 2 — Traces" with 4 filled indicators. Top (fresh): "Layer 3 — Trace Attributes" with 4 sub-labels: "1. What attributes are", "2. Static (agent-level)", "3. Dynamic (hooks)", "4. Business language layer", all with empty indicators.

**Animation notes**:
- Layer 3 card slides in from above on 5:35 and lands on top of the (dimmed) stack.
- Sub-label indicators fill in as concepts progress.

---

### Diagram 4.2 — Static vs dynamic attributes (comparison)

**Purpose**: Muestra la diferencia entre los dos mecanismos.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> Split-screen composition, 16:9. Vertical divider. LEFT half labeled "STATIC" (bold header). Below: a picture of an agent creation moment (small "Agent" icon), with a tag being pinned to it that says "session.id: my-session". Below, arrows radiating out to many span icons (indicating the tag applies to all of them). LEFT-side accent: Strands orange. RIGHT half labeled "DYNAMIC" (bold header). Below: a specific tool span icon lit up mid-execution with a hook icon (small circular arrow) firing onto it, adding a fresh tag "business.vip_booking: true". Only THAT specific span gets the tag. RIGHT-side accent: AWS blue. Bottom caption spanning both sides: "Two ways to add your own context to the trace."

**Animation notes**:
- LEFT side reveals first on 6:18: agent + static tag being pinned + spans lighting up all at once.
- RIGHT side reveals on 6:48: a single tool span gets lit up while others stay dim; hook icon fires onto it; new tag appears on that single span.
- Bottom caption fades in on 7:10.

---

### Diagram 4.3 — Business context on a trace

**Purpose**: El punto final — atributos del SDK vs atributos del negocio conviviendo en el mismo span.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> A single zoomed "execute_tool book_flight span" card, centered on 16:9 white background. The card is divided into two sections stacked vertically with a subtle divider:
>
> UPPER section labeled "What the SDK knows" (grey header): monospace list of key-value attributes: "gen_ai.tool.name: book_flight", "gen_ai.tool.status: success", "gen_ai.tool.call.id: abc-123".
>
> LOWER section labeled "What YOU know" (Strands orange header): monospace list: "business.booking_amount_usd: 88.73", "business.vip_booking: true", "session.id: my-session".
>
> A small annotation on the side with an arrow pointing to the lower section: "Added by your hook. Never sent to the model."
>
> Both sections have subtle backgrounds to distinguish them: upper light grey, lower light orange tint.

**Animation notes**:
- Upper section reveals on 7:20 (SDK knows).
- Divider draws itself on 7:22.
- Lower section reveals on 7:23 (YOU know).
- Annotation with arrow fades in on 7:25.

---

## Section 1 (UPDATED) — Hook: "running agents blind" (0:00–0:55)

> Note: the hook script changed — pain-first opening. Diagram 1.1 (server dashboard) still applies but moves later in the section. New opening b-roll below.

### Diagram 1.0 — The blind agent (opening b-roll, ~0:03–0:15)

**Purpose**: Visualizar el dolor del hook: el agente en producción que hace cosas que no podés explicar.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> 16:9 frame (1920×1080). A dark-tinted scene (this one frame can be darker than the rest for drama): a stylized user icon on the left sends a chat bubble with a short question ("One simple question…"). In the center, a large agent icon (robot head or hexagon) with FIVE arrows shooting out of it in different directions toward five generic tool icons, each arrow drawn as a tangled, chaotic path. Above the agent, a large timer reading "00:30". On the right, a chat bubble with a long confusing answer, rendered as scribbled lines. Bottom caption in bold: "What did it actually do?". Grey/desaturated palette with one red accent on the timer.

**Animation notes**:
- User bubble appears on 0:03.
- Arrows shoot out one by one, fast, chaotic (0:05–0:10).
- Timer counts up. Answer bubble lands on 0:12.
- Caption "What did it actually do?" punches in on 0:13.

---

### Diagram 1.4 — Morgan course card (~0:38)

**Purpose**: Momento en que Eli menciona el curso de Morgan.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> 16:9 frame (1920×1080), white background. A lower-third banner card: rounded rectangle spanning about 60% of the frame width, anchored to the bottom of the canvas. White card with Strands orange left border (8px). Text: "Want to go deeper on Strands? Full course by Morgan — link in the comments". Small play-button icon on the left. Clean, unobtrusive.

**Animation notes**:
- Slides in from the left at 0:38, holds 5 seconds, slides out.

---

## Section 2 — OpenTelemetry: the standard underneath (0:55–1:25)

### Diagram 2.0 — OTEL: three signals, two worlds

**Purpose**: El único diagrama de esta sección: OTEL define traces/metrics/logs, y para agentes el contenido cambia.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> 16:9 frame (1920×1080). A centered composition. Top: the OpenTelemetry name in bold dark text with a subtle telescope icon (or simply "OpenTelemetry · OTEL"). Below it, three columns, one per signal. Column 1 header "Traces", column 2 header "Metrics", column 3 header "Logs". Each column has TWO stacked rows: the top row labeled "Traditional software" in grey showing: "stack traces" (col 1), "memory usage" (col 2), "error logs" (col 3). The bottom row labeled "AI agents" in Strands orange showing: "reasoning steps" (col 1), "token usage" (col 2), "tool decisions" (col 3). A subtle arrow from the grey row down to the orange row in each column, suggesting the same signal carrying new content. Bottom caption: "Same standard. Different content. Any framework."

**Animation notes**:
- "OpenTelemetry · OTEL" title lands on 0:58.
- Three column headers appear together on 1:02 as Eli says "traces, metrics, and logs".
- Grey "traditional" row fades in on 1:06.
- Orange "AI agents" row replaces/slides under it on 1:10, item by item in sync with Eli ("reasoning steps instead of stack traces, token usage instead of memory usage, tool decisions instead of function calls").
- Bottom caption on 1:20 as Eli says it works with any framework.

---

## Section 6 — Production: AgentCore Observability (8:10–11:00)

### Diagram 6.1 — From terminal to production

**Purpose**: Transición del hook: todo lo construido vivía en la terminal; ahora se va a producción.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> 16:9 frame (1920×1080). Split composition with an arrow between the halves. LEFT: a stylized terminal window (dark background, a few lines of green/white monospace text suggesting spans and metrics output), labeled underneath "Development — your terminal". RIGHT: a stylized cloud environment: the AWS cloud silhouette containing a small agent icon, labeled underneath "Production — Amazon Bedrock AgentCore". A large arrow from left to right labeled "same agent, zero config changes". LEFT side grey/dark tones, RIGHT side AWS blue with orange accents.

**Animation notes**:
- Left terminal appears on 8:12.
- Arrow draws on 8:20.
- Right cloud lands on 8:25.

---

### Diagram 6.2 — Production architecture

**Purpose**: Cómo queda el sistema en producción: Runtime + Gateway + Lambdas + DynamoDB.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> 16:9 frame (1920×1080). Architecture diagram, left-to-right flow. Far left: user icon with a chat bubble. Arrow to a large rounded rectangle labeled "AgentCore Runtime" containing a smaller box "Travel Agent (Strands)" — this box has a subtle OpenTelemetry badge pinned to its corner reading "auto-instrumented". Arrow from the runtime to a vertical rounded rectangle labeled "AgentCore Gateway (MCP)". From the gateway, three arrows to three Lambda function icons (the AWS Lambda orange lambda symbol): "search_flights", "get_weather", "book_flight". From the book_flight Lambda, one more arrow to a DynamoDB icon labeled "FlightBookings". Bottom of the frame, a wide horizontal band in AWS blue labeled "Amazon CloudWatch — GenAI Observability" with small arrows flowing DOWN into it from the Runtime, the Gateway, and the Lambdas — suggesting all telemetry lands there.

**Animation notes**:
- Build left to right as Eli describes: user → runtime (8:40) → gateway (8:50) → lambdas + dynamo (8:55).
- The CloudWatch band at the bottom lights up at 9:05 when Eli transitions to "where does everything land".

---

### Diagram 6.3 — The three views of GenAI Observability

**Purpose**: Walkthrough visual de Agents View → Sessions View → Traces View. (En el video real esto será screen capture de la consola; este diagrama es el fallback/apoyo.)

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> 16:9 frame (1920×1080). Three browser-window mockups arranged in a horizontal row, each representing a CloudWatch console view. Window 1 titled "Agents View": a table listing three agent rows with mini columns for invocations, latency, errors — one row highlighted. Window 2 titled "Sessions View": a list of session entries with timestamps, one session expanded showing a conversation icon. Window 3 titled "Traces View": a horizontal flame-graph/timeline with nested colored bars (top bar orange labeled "invoke_agent", below it grey bars "cycle", inside them blue "chat" and green "execute_tool" bars) — visually echoing the span tree from Section 4. Each window has a simplified CloudWatch header bar. Label under the row: "CloudWatch → GenAI Observability".

**Animation notes**:
- Window 1 slides in on 9:10 (Agents View narration).
- Window 2 slides in on 9:30 (Sessions View).
- Window 3 slides in on 9:55 — zoom into it briefly, since it echoes the Layer 2 span tree.
- Optional: when Eli mentions the session ID from Layer 3 (~9:45), a small orange tag "session.id" pulses on Window 2.

---

### Diagram 6.4 — Gateway observability: TargetExecutionTime

**Purpose**: El concepto estrella del gateway: cuánto del tiempo total fue tu Lambda vs el plumbing.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> 16:9 frame (1920×1080). A horizontal stacked bar visualization. Title: "One tool call, decomposed". A single wide horizontal bar divided into two segments: a small grey segment labeled "Gateway overhead" and a large orange segment labeled "TargetExecutionTime — your Lambda". Below the bar, a bracket spanning the whole width labeled "Duration (total)". To the right, a callout box: "Slow tool? Now you know WHERE it's slow." Below, a small list of the other gateway metrics as small chips: "Invocations", "Throttles", "Latency", "SystemErrors", "UserErrors" — each a small rounded chip in grey. Bottom note in italic: "CloudWatch namespace: AWS/Bedrock-AgentCore".

**Animation notes**:
- The full bar draws first (10:00) labeled Duration.
- It splits into the two segments on 10:08 as Eli explains TargetExecutionTime.
- Callout pops on 10:15.
- Metric chips fade in on 10:20.

---

### Diagram 6.5 — One connected story (traces linking)

**Purpose**: El cierre del Concepto 3: spans del gateway conectan con la traza del agente.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> 16:9 frame (1920×1080). A vertical flow of connected spans, like a simplified trace timeline. Top: an orange span bar "invoke_agent — the user's question". Below, connected by a vertical line: a grey span "execute_tool book_flight (agent side)". Below that: a blue span "Gateway: Call Tool (kind SERVER)". Below that: a teal span "Gateway: Lambda target (kind CLIENT)". At the bottom: a green span "Lambda: book_flight handler". All five bars share one vertical connector line on the left labeled "same trace_id". Caption at the bottom: "From the user's question to the Lambda that answered it — one connected story."

**Animation notes**:
- Spans appear top to bottom, one by one (10:25–10:35), the connector line drawing downward as they land.
- Caption fades in on 10:38.

---

## Section 7 — Wrap (11:00–11:30)

### Diagram 7.1 — The three layers, complete

**Purpose**: Recap visual — la pila completa de 3 capas que se construyó durante el video.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> 16:9 frame (1920×1080). The final "stack" image: three stacked pillar cards, all fully lit (no dimming). Bottom: "Layer 1 — Metrics · what it did, how efficiently" with a dollar/gauge icon. Middle: "Layer 2 — Traces · the path it took" with a tree icon. Top: "Layer 3 — Trace Attributes · in your business language" with a tag icon. To the right of the stack, three small logos/badges vertically: "Strands Agents" (orange), "OpenTelemetry" (grey), "Amazon Bedrock AgentCore" (AWS blue), with a thin arrow flowing from the stack through the three badges downward, labeled "build → carry → serve". Clean, celebratory but sober.

**Animation notes**:
- The three layer cards assemble quickly (11:00–11:08), bottom-up, echoing how they appeared during the video.
- The three badges light up in order on 11:08–11:12 as Eli says "built with Strands, carried by OpenTelemetry, served by AgentCore".

---

### Diagram 7.2 — CTA end card

**Purpose**: Cierre con repo + curso de Morgan.

**Canva AI prompt**:
> [PASTE STYLE BLOCK]
> 16:9 frame (1920×1080), white background. YouTube end-card style layout — two large rounded-rectangle cards side by side. Left card: placeholder for a video thumbnail labeled "Sample repository — link in description" with a GitHub-style repo icon and a small folder tree suggestion (01, 02, 03, 04 folders). Right card: "Strands full course by Morgan — link below" with a play icon. Bottom center: text "Stop running your agents blind." in bold. Keep generous margins around the edges (YouTube overlays UI there).

**Animation notes**:
- Both cards fade in on 11:15.
- Bottom text lands on 11:22 in sync with the voiceover's last line.
