import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const W = 1280;
const H = 720;
const COLORS = {
  paper: "#F7F5F0",
  ink: "#15202B",
  navy: "#0B2C5F",
  cyan: "#23A6C7",
  coral: "#F06455",
  mist: "#D8E0E7",
  gray: "#65717E",
  light: "#E9E6DF",
  white: "#FFFFFF",
  green: "#3B8C78",
};

const buildRoot = process.env.DEMO_BUILD_ROOT;
const outputRoot = process.env.DEMO_OUTPUT_ROOT;
if (!buildRoot || !outputRoot) {
  throw new Error("DEMO_BUILD_ROOT and DEMO_OUTPUT_ROOT are required");
}

async function writeBlob(filePath, blob) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

function addText(slide, text, position, style = {}, name = "text") {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    fontSize: 18,
    color: COLORS.ink,
    fontFamily: "Arial",
    ...style,
  };
  return shape;
}

function addRule(slide, left, top, width, color = COLORS.mist, height = 2) {
  return slide.shapes.add({
    geometry: "rect",
    position: { left, top, width, height },
    fill: color,
    line: { style: "solid", fill: color, width: 0 },
  });
}

function addHeader(slide, title, section, page) {
  addText(
    slide,
    section.toUpperCase(),
    { left: 64, top: 34, width: 420, height: 22 },
    { fontSize: 12, bold: true, color: COLORS.cyan, letterSpacing: 1.2 },
    `section-${page}`,
  );
  addText(
    slide,
    title,
    { left: 64, top: 67, width: 1120, height: 90 },
    { fontSize: 36, bold: true, color: COLORS.ink },
    `title-${page}`,
  );
  addRule(slide, 64, 166, 1152, COLORS.mist, 1);
}

function addFooter(slide, page) {
  addRule(slide, 64, 670, 1152, COLORS.mist, 1);
  addText(
    slide,
    "Synthetic demonstration data • Consulting Deck v0.2",
    { left: 64, top: 681, width: 620, height: 18 },
    { fontSize: 10, color: COLORS.gray },
    `source-${page}`,
  );
  addText(
    slide,
    String(page).padStart(2, "0"),
    { left: 1150, top: 681, width: 66, height: 18 },
    { fontSize: 10, color: COLORS.gray, alignment: "right" },
    `page-${page}`,
  );
  slide.speakerNotes.textFrame.setText(
    "[Sources]\n- Synthetic demonstration data created for Consulting Deck v0.2. Not a real-world benchmark or forecast.",
  );
}

function addCover(slide, eyebrow, title, subtitle, accent, proof) {
  slide.background.fill = COLORS.paper;
  addText(
    slide,
    eyebrow.toUpperCase(),
    { left: 72, top: 68, width: 520, height: 28 },
    { fontSize: 13, bold: true, color: accent, letterSpacing: 1.4 },
    "cover-eyebrow",
  );
  addText(
    slide,
    title,
    { left: 72, top: 150, width: 790, height: 190 },
    { fontSize: 58, bold: true, color: COLORS.ink },
    "cover-title",
  );
  addText(
    slide,
    subtitle,
    { left: 72, top: 366, width: 700, height: 88 },
    { fontSize: 22, color: COLORS.gray },
    "cover-subtitle",
  );
  addRule(slide, 72, 512, 1136, COLORS.navy, 3);
  addText(
    slide,
    proof,
    { left: 72, top: 542, width: 860, height: 54 },
    { fontSize: 17, bold: true, color: COLORS.navy },
    "cover-proof",
  );
  addText(
    slide,
    "EDITABLE PPTX DEMO",
    { left: 956, top: 548, width: 252, height: 28 },
    { fontSize: 12, bold: true, color: accent, alignment: "right" },
    "cover-tag",
  );
  addText(
    slide,
    "Synthetic data for product demonstration",
    { left: 956, top: 579, width: 252, height: 24 },
    { fontSize: 10, color: COLORS.gray, alignment: "right" },
    "cover-source",
  );
  slide.speakerNotes.textFrame.setText(
    "[Sources]\n- Synthetic demonstration data created for Consulting Deck v0.2. Not a real-world benchmark or forecast.",
  );
}

function addInsight(slide, number, label, body, left, top, color = COLORS.navy) {
  addText(
    slide,
    number,
    { left, top, width: 220, height: 70 },
    { fontSize: 46, bold: true, color },
    `metric-${number}-${left}`,
  );
  addText(
    slide,
    label,
    { left, top: top + 66, width: 240, height: 36 },
    { fontSize: 16, bold: true, color: COLORS.ink },
  );
  addText(
    slide,
    body,
    { left, top: top + 106, width: 246, height: 64 },
    { fontSize: 13, color: COLORS.gray },
  );
}

function addCallout(slide, text, left, top, width, color = COLORS.coral) {
  addRule(slide, left, top, 5, color, 78);
  addText(
    slide,
    text,
    { left: left + 18, top: top - 2, width: width - 18, height: 82 },
    { fontSize: 18, bold: true, color: COLORS.ink },
  );
}

function basePresentation() {
  return Presentation.create({ slideSize: { width: W, height: H } });
}

function buildAiDeck() {
  const p = basePresentation();

  let slide = p.slides.add();
  addCover(
    slide,
    "AI value realization",
    "AI value is broad in theory — but concentrated in execution",
    "A six-page consulting demonstration showing how evidence, analytical charts and an action storyline become an editable PowerPoint.",
    COLORS.cyan,
    "The modeled portfolio shifts investment from scattered pilots to four repeatable workflows.",
  );

  slide = p.slides.add();
  slide.background.fill = COLORS.paper;
  addHeader(slide, "Adoption is broad, but measurable value remains concentrated", "Where value sits", 2);
  slide.charts.add("bar", {
    position: { left: 64, top: 190, width: 735, height: 408 },
    categories: ["Customer service", "Software delivery", "Marketing", "Risk operations", "Finance", "HR"],
    series: [
      { name: "Experimenting", values: [24, 28, 25, 23, 20, 18], fill: COLORS.mist },
      { name: "Scaled", values: [52, 43, 36, 31, 21, 16], fill: COLORS.cyan },
    ],
    barOptions: { direction: "bar", grouping: "stacked", gapWidth: 40 },
    hasLegend: true,
    legend: { position: "bottom", overlay: false, textStyle: { fontSize: 12, fill: COLORS.gray } },
    xAxis: { min: 0, max: 90, majorUnit: 20, numberFormatCode: "0", title: { text: "Share of initiatives, %", textStyle: { fontSize: 11, fill: COLORS.gray } }, textStyle: { fontSize: 11, fill: COLORS.gray }, majorGridlines: { style: "dashed", fill: COLORS.mist, width: 1 } },
    yAxis: { textStyle: { fontSize: 13, fill: COLORS.ink }, line: { style: "solid", fill: COLORS.mist, width: 1 } },
    chartFill: "none",
    plotAreaFill: "none",
    chartLine: { style: "solid", fill: "none", width: 0 },
  });
  addInsight(slide, "3.2×", "Value concentration", "Scaled customer-service workflows generate more modeled value than the median function.", 886, 206, COLORS.coral);
  addInsight(slide, "68%", "Still experimental", "Most initiatives have not crossed into repeatable operating routines.", 886, 405, COLORS.navy);
  addFooter(slide, 2);

  slide = p.slides.add();
  slide.background.fill = COLORS.paper;
  addHeader(slide, "Four repeatable workflows account for nearly three-quarters of modeled value", "Portfolio focus", 3);
  slide.charts.add("bar", {
    position: { left: 64, top: 185, width: 810, height: 410 },
    categories: ["Service resolution", "Developer copilot", "Campaign content", "Risk review", "Knowledge search", "Other pilots"],
    series: [{
      name: "Share of modeled annual value",
      values: [24, 19, 16, 13, 10, 18],
      fill: COLORS.navy,
      points: [
        { idx: 0, fill: COLORS.coral },
        { idx: 1, fill: COLORS.coral },
        { idx: 2, fill: COLORS.cyan },
        { idx: 3, fill: COLORS.cyan },
        { idx: 4, fill: COLORS.mist },
        { idx: 5, fill: COLORS.mist },
      ],
    }],
    barOptions: { direction: "bar", grouping: "clustered", gapWidth: 42 },
    hasLegend: false,
    dataLabels: { showValue: true, position: "outEnd", textStyle: { fontSize: 13, bold: true, fill: COLORS.ink } },
    xAxis: { min: 0, max: 28, majorUnit: 7, numberFormatCode: "0", title: { text: "Share of modeled annual value, %", textStyle: { fontSize: 11, fill: COLORS.gray } }, textStyle: { fontSize: 11, fill: COLORS.gray }, majorGridlines: { style: "dashed", fill: COLORS.mist, width: 1 } },
    yAxis: { textStyle: { fontSize: 13, fill: COLORS.ink }, line: { style: "solid", fill: COLORS.mist, width: 1 } },
    chartFill: "none",
    plotAreaFill: "none",
    chartLine: { style: "solid", fill: "none", width: 0 },
  });
  addCallout(slide, "72% of modeled value comes from the first four workflows — the portfolio does not need another broad pilot wave.", 925, 235, 265, COLORS.coral);
  addText(slide, "Implication", { left: 925, top: 390, width: 180, height: 28 }, { fontSize: 13, bold: true, color: COLORS.cyan });
  addText(slide, "Fund reusable workflow assets, not disconnected model experiments.", { left: 925, top: 425, width: 255, height: 92 }, { fontSize: 23, bold: true, color: COLORS.navy });
  addFooter(slide, 3);

  slide = p.slides.add();
  slide.background.fill = COLORS.paper;
  addHeader(slide, "Operating-model gaps now outweigh model-access constraints", "What blocks scale", 4);
  slide.charts.add("bar", {
    position: { left: 64, top: 195, width: 720, height: 400 },
    categories: ["Workflow ownership", "Data readiness", "Risk controls", "Change adoption", "Model quality", "Infrastructure"],
    series: [{
      name: "Share citing as primary bottleneck",
      values: [27, 23, 18, 15, 10, 7],
      fill: COLORS.navy,
      points: [
        { idx: 0, fill: COLORS.coral },
        { idx: 1, fill: COLORS.coral },
        { idx: 2, fill: COLORS.cyan },
        { idx: 3, fill: COLORS.cyan },
      ],
    }],
    barOptions: { direction: "bar", grouping: "clustered", gapWidth: 44 },
    hasLegend: false,
    dataLabels: { showValue: true, position: "outEnd", textStyle: { fontSize: 13, bold: true, fill: COLORS.ink } },
    xAxis: { min: 0, max: 32, majorUnit: 8, numberFormatCode: "0", title: { text: "Share citing as primary bottleneck, %", textStyle: { fontSize: 11, fill: COLORS.gray } }, textStyle: { fontSize: 11, fill: COLORS.gray }, majorGridlines: { style: "dashed", fill: COLORS.mist, width: 1 } },
    yAxis: { textStyle: { fontSize: 13, fill: COLORS.ink } },
    chartFill: "none",
    plotAreaFill: "none",
    chartLine: { style: "solid", fill: "none", width: 0 },
  });
  addText(slide, "65%", { left: 872, top: 220, width: 260, height: 82 }, { fontSize: 62, bold: true, color: COLORS.coral });
  addText(slide, "of primary bottlenecks sit in ownership, data or controls", { left: 872, top: 306, width: 275, height: 74 }, { fontSize: 20, bold: true, color: COLORS.ink });
  addCallout(slide, "The next unlock is governance embedded in the workflow — not another standalone model evaluation.", 872, 430, 290, COLORS.cyan);
  addFooter(slide, 4);

  slide = p.slides.add();
  slide.background.fill = COLORS.paper;
  addHeader(slide, "A stage-gated portfolio more than doubles value capture within three quarters", "How to scale", 5);
  slide.charts.add("line", {
    position: { left: 64, top: 200, width: 795, height: 385 },
    categories: ["Q0", "Q1", "Q2", "Q3"],
    series: [
      { name: "Stage-gated portfolio", values: [18, 32, 49, 68], line: { style: "solid", fill: COLORS.coral, width: 4 }, marker: { symbol: "circle", size: 8 } },
      { name: "Broad pilot portfolio", values: [18, 24, 27, 29], line: { style: "solid", fill: COLORS.navy, width: 3 }, marker: { symbol: "circle", size: 7 } },
    ],
    hasLegend: true,
    legend: { position: "bottom", overlay: false, textStyle: { fontSize: 12, fill: COLORS.gray } },
    xAxis: { textStyle: { fontSize: 12, fill: COLORS.gray }, line: { style: "solid", fill: COLORS.mist, width: 1 } },
    yAxis: { min: 0, max: 80, majorUnit: 20, title: { text: "Modeled value index", textStyle: { fontSize: 12, fill: COLORS.gray } }, textStyle: { fontSize: 11, fill: COLORS.gray }, majorGridlines: { style: "dashed", fill: COLORS.mist, width: 1 } },
    chartFill: "none",
    plotAreaFill: "none",
    chartLine: { style: "solid", fill: "none", width: 0 },
  });
  addInsight(slide, "+134%", "Value advantage", "Stage gates concentrate funding behind workflows that prove adoption and control readiness.", 922, 225, COLORS.coral);
  addText(slide, "Decision rule", { left: 922, top: 436, width: 190, height: 26 }, { fontSize: 13, bold: true, color: COLORS.cyan });
  addText(slide, "Scale only when usage, unit economics and controls all clear the gate.", { left: 922, top: 472, width: 260, height: 92 }, { fontSize: 20, bold: true, color: COLORS.navy });
  addFooter(slide, 5);

  slide = p.slides.add();
  slide.background.fill = COLORS.paper;
  addHeader(slide, "The first 90 days should lock two workflows and the operating system around them", "Action agenda", 6);
  const phases = [
    { n: "01", title: "Choose", weeks: "Weeks 1–2", body: "Select two workflows with clear owners, baseline economics and measurable adoption.", color: COLORS.coral },
    { n: "02", title: "Instrument", weeks: "Weeks 3–5", body: "Build evaluation, risk controls and usage telemetry into the working process.", color: COLORS.cyan },
    { n: "03", title: "Scale", weeks: "Weeks 6–10", body: "Redesign roles, train teams and fund reusable workflow components.", color: COLORS.navy },
    { n: "04", title: "Reallocate", weeks: "Weeks 11–13", body: "Stop weak pilots and move capacity toward proven value pools.", color: COLORS.green },
  ];
  phases.forEach((phase, i) => {
    const left = 64 + i * 287;
    addRule(slide, left, 218, 258, phase.color, 5);
    addText(slide, phase.n, { left, top: 246, width: 52, height: 32 }, { fontSize: 16, bold: true, color: phase.color });
    addText(slide, phase.title, { left, top: 292, width: 230, height: 40 }, { fontSize: 26, bold: true, color: COLORS.ink });
    addText(slide, phase.weeks, { left, top: 344, width: 220, height: 25 }, { fontSize: 13, bold: true, color: COLORS.gray });
    addText(slide, phase.body, { left, top: 392, width: 238, height: 112 }, { fontSize: 16, color: COLORS.ink });
  });
  addCallout(slide, "Board decision: approve the two-workflow portfolio and assign one accountable business owner per workflow.", 64, 560, 1120, COLORS.coral);
  addFooter(slide, 6);
  return p;
}

function buildBankingDeck() {
  const p = basePresentation();

  let slide = p.slides.add();
  addCover(
    slide,
    "Retail banking growth",
    "Primary relationships — not acquisition volume — drive the growth gap",
    "A six-page consulting demonstration connecting customer economics, journey leakage and a focused growth agenda in an editable PowerPoint.",
    COLORS.coral,
    "The modeled plan reallocates investment toward high-potential households and three decisive journeys.",
  );

  slide = p.slides.add();
  slide.background.fill = COLORS.paper;
  addHeader(slide, "Most of the growth gap comes after acquisition, not before it", "Diagnose the gap", 2);
  slide.charts.add("bar", {
    position: { left: 64, top: 190, width: 820, height: 410 },
    categories: ["Starting base", "New customers", "Activation", "Primary status", "Cross-sell", "Attrition"],
    series: [{
      name: "Growth contribution",
      values: [3.2, 1.1, 0.7, 2.4, 1.3, -0.8],
      fill: COLORS.navy,
      points: [
        { idx: 1, fill: COLORS.mist },
        { idx: 2, fill: COLORS.cyan },
        { idx: 3, fill: COLORS.coral },
        { idx: 4, fill: COLORS.coral },
        { idx: 5, fill: COLORS.gray },
      ],
    }],
    barOptions: { direction: "column", grouping: "clustered", gapWidth: 52 },
    hasLegend: false,
    dataLabels: { showValue: true, position: "outEnd", textStyle: { fontSize: 12, bold: true, fill: COLORS.ink } },
    xAxis: { textStyle: { fontSize: 11, fill: COLORS.gray } },
    yAxis: { min: -1, max: 4, majorUnit: 1, numberFormatCode: "0.0", title: { text: "Growth contribution, percentage points", textStyle: { fontSize: 11, fill: COLORS.gray } }, textStyle: { fontSize: 11, fill: COLORS.gray }, majorGridlines: { style: "dashed", fill: COLORS.mist, width: 1 } },
    chartFill: "none",
    plotAreaFill: "none",
    chartLine: { style: "solid", fill: "none", width: 0 },
  });
  addInsight(slide, "61%", "Post-acquisition gap", "Primary status and cross-sell explain most of the modeled upside.", 930, 220, COLORS.coral);
  addCallout(slide, "Acquisition matters, but the larger prize is converting an acquired customer into a primary relationship.", 930, 424, 258, COLORS.cyan);
  addFooter(slide, 2);

  slide = p.slides.add();
  slide.background.fill = COLORS.paper;
  addHeader(slide, "Primary customers create 4.1× more relationship value", "Customer economics", 3);
  slide.charts.add("bar", {
    position: { left: 64, top: 195, width: 785, height: 405 },
    categories: ["Primary", "Multi-product", "Single-product", "Dormant"],
    series: [{
      name: "Annual relationship value index",
      values: [410, 235, 100, 32],
      fill: COLORS.navy,
      points: [
        { idx: 0, fill: COLORS.coral },
        { idx: 1, fill: COLORS.cyan },
        { idx: 2, fill: COLORS.mist },
        { idx: 3, fill: COLORS.light },
      ],
    }],
    barOptions: { direction: "bar", grouping: "clustered", gapWidth: 52 },
    hasLegend: false,
    dataLabels: { showValue: true, position: "outEnd", textStyle: { fontSize: 14, bold: true, fill: COLORS.ink } },
    xAxis: { min: 0, max: 460, majorUnit: 100, textStyle: { fontSize: 11, fill: COLORS.gray }, majorGridlines: { style: "dashed", fill: COLORS.mist, width: 1 } },
    yAxis: { textStyle: { fontSize: 14, fill: COLORS.ink } },
    chartFill: "none",
    plotAreaFill: "none",
    chartLine: { style: "solid", fill: "none", width: 0 },
  });
  addText(slide, "The economics are nonlinear", { left: 930, top: 226, width: 250, height: 34 }, { fontSize: 15, bold: true, color: COLORS.cyan });
  addText(slide, "Primary status raises balances, product depth and retention at the same time.", { left: 930, top: 275, width: 250, height: 112 }, { fontSize: 24, bold: true, color: COLORS.navy });
  addCallout(slide, "Growth management should optimize relationship migration, not only product conversion.", 930, 455, 260, COLORS.coral);
  addFooter(slide, 3);

  slide = p.slides.add();
  slide.background.fill = COLORS.paper;
  addHeader(slide, "Three customer journeys leak nearly two-thirds of the cross-sell opportunity", "Journey leakage", 4);
  slide.charts.add("bar", {
    position: { left: 64, top: 190, width: 740, height: 420 },
    categories: ["Eligible households", "Relevant offer", "Engaged", "Applied", "Activated"],
    series: [{
      name: "Households",
      values: [100, 78, 51, 34, 21],
      fill: COLORS.cyan,
      points: [
        { idx: 0, fill: COLORS.navy },
        { idx: 1, fill: "#167FA8" },
        { idx: 2, fill: COLORS.cyan },
        { idx: 3, fill: "#78C4D5" },
        { idx: 4, fill: COLORS.mist },
      ],
    }],
    barOptions: { direction: "bar", grouping: "clustered", gapWidth: 26 },
    hasLegend: false,
    dataLabels: { showValue: true, position: "outEnd", textStyle: { fontSize: 13, bold: true, fill: COLORS.ink } },
    xAxis: { min: 0, max: 110, majorUnit: 25, title: { text: "Indexed households", textStyle: { fontSize: 11, fill: COLORS.gray } }, textStyle: { fontSize: 11, fill: COLORS.gray }, majorGridlines: { style: "dashed", fill: COLORS.mist, width: 1 } },
    yAxis: { textStyle: { fontSize: 13, fill: COLORS.ink } },
    chartFill: "none",
    plotAreaFill: "none",
    chartLine: { style: "solid", fill: "none", width: 0 },
  });
  const leakages = [
    ["−22 pts", "Offer relevance", "Eligibility rules are broad; next-best-action logic is weak."],
    ["−27 pts", "Engagement", "Outreach is product-led rather than event-led."],
    ["−13 pts", "Activation", "The first-use journey does not reinforce the relationship."],
  ];
  leakages.forEach((item, i) => addInsight(slide, item[0], item[1], item[2], 892, 194 + i * 145, i === 1 ? COLORS.coral : COLORS.navy));
  addFooter(slide, 4);

  slide = p.slides.add();
  slide.background.fill = COLORS.paper;
  addHeader(slide, "A segment-led model shifts investment toward households with headroom and intent", "Where to invest", 5);
  slide.charts.add("bubble", {
    position: { left: 64, top: 185, width: 805, height: 420 },
    series: [
      { name: "Emerging affluent", xValues: [74], values: [78], bubbleSizes: [48], fill: COLORS.coral, marker: { symbol: "circle", size: 14 } },
      { name: "Young professionals", xValues: [67], values: [70], bubbleSizes: [40], fill: COLORS.cyan, marker: { symbol: "circle", size: 13 } },
      { name: "Established families", xValues: [55], values: [62], bubbleSizes: [58], fill: COLORS.navy, marker: { symbol: "circle", size: 16 } },
      { name: "Mass active", xValues: [40], values: [38], bubbleSizes: [72], fill: COLORS.mist, marker: { symbol: "circle", size: 18 } },
      { name: "Low-engagement", xValues: [22], values: [24], bubbleSizes: [45], fill: COLORS.light, marker: { symbol: "circle", size: 14 } },
    ],
    scatterOptions: { style: "marker", varyColors: true },
    hasLegend: true,
    legend: { position: "bottom", overlay: false, textStyle: { fontSize: 10, fill: COLORS.gray } },
    xAxis: { min: 0, max: 100, majorUnit: 20, title: { text: "Relationship headroom", textStyle: { fontSize: 12, fill: COLORS.gray } }, textStyle: { fontSize: 11, fill: COLORS.gray }, majorGridlines: { style: "dashed", fill: COLORS.mist, width: 1 } },
    yAxis: { min: 0, max: 100, majorUnit: 20, title: { text: "Engagement intent", textStyle: { fontSize: 12, fill: COLORS.gray } }, textStyle: { fontSize: 11, fill: COLORS.gray }, majorGridlines: { style: "dashed", fill: COLORS.mist, width: 1 } },
    chartFill: "none",
    plotAreaFill: "none",
    chartLine: { style: "solid", fill: "none", width: 0 },
  });
  addText(slide, "Priority pool", { left: 930, top: 220, width: 240, height: 30 }, { fontSize: 14, bold: true, color: COLORS.coral });
  addText(slide, "Emerging affluent and young professionals combine high intent with relationship headroom.", { left: 930, top: 266, width: 250, height: 142 }, { fontSize: 24, bold: true, color: COLORS.navy });
  addCallout(slide, "Use segment economics to set journey investment and service intensity.", 930, 474, 260, COLORS.cyan);
  addFooter(slide, 5);

  slide = p.slides.add();
  slide.background.fill = COLORS.paper;
  addHeader(slide, "Four moves can add 9–12 points to modeled wallet share", "Growth agenda", 6);
  const moves = [
    ["01", "Detect life events", "2–3 pts", COLORS.coral],
    ["02", "Personalize next best action", "3–4 pts", COLORS.cyan],
    ["03", "Redesign first 30 days", "2–3 pts", COLORS.navy],
    ["04", "Reward relationship depth", "2 pts", COLORS.green],
  ];
  moves.forEach((item, i) => {
    const top = 200 + i * 100;
    addText(slide, item[0], { left: 64, top, width: 54, height: 34 }, { fontSize: 15, bold: true, color: item[3] });
    addText(slide, item[1], { left: 130, top: top - 4, width: 390, height: 42 }, { fontSize: 23, bold: true, color: COLORS.ink });
    addRule(slide, 545, top + 10, 370, COLORS.light, 14);
    const barWidth = [240, 320, 250, 180][i];
    addRule(slide, 545, top + 10, barWidth, item[3], 14);
    addText(slide, item[2], { left: 940, top: top - 2, width: 120, height: 34 }, { fontSize: 18, bold: true, color: item[3], alignment: "right" });
  });
  addText(slide, "9–12 pts", { left: 940, top: 560, width: 230, height: 58 }, { fontSize: 44, bold: true, color: COLORS.coral, alignment: "right" });
  addText(slide, "modeled wallet-share upside", { left: 940, top: 617, width: 230, height: 25 }, { fontSize: 13, bold: true, color: COLORS.gray, alignment: "right" });
  addFooter(slide, 6);
  return p;
}

async function exportDeck(presentation, slug, pptxName) {
  const buildDir = path.join(buildRoot, slug);
  const finalDir = path.join(outputRoot, slug);
  const renderDir = path.join(finalDir, "renders");
  await fs.mkdir(buildDir, { recursive: true });
  await fs.mkdir(renderDir, { recursive: true });

  for (const [index, slide] of presentation.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    await writeBlob(path.join(renderDir, `${stem}.png`), await presentation.export({ slide, format: "png", scale: 1.5 }));
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(path.join(buildDir, `${stem}.layout.json`), await layout.text());
  }
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(path.join(finalDir, pptxName));
  const inspection = await presentation.inspect({ kind: "slide,textbox,shape,chart,notes", maxChars: 50000 });
  await fs.writeFile(path.join(buildDir, "inspection.ndjson"), inspection.ndjson);
}

await exportDeck(buildAiDeck(), "ai-value-realization", "ai-value-realization-demo.pptx");
await exportDeck(buildBankingDeck(), "retail-banking-growth", "retail-banking-growth-demo.pptx");
