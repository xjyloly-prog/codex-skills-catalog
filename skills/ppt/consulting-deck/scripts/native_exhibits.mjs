/** Original native PowerPoint exhibit components.
 * The host supplies Artifact Tool slide objects; this module never loads packages,
 * starts services, accesses the network, or mutates canonical project inputs.
 * Canvas/font geometry uses CSS pixels (96 dpi).
 */
export const palette = Object.freeze({
  ink: '#111820', navy: '#0B2D52', blue: '#1687C7', sky: '#67C5E8',
  muted: '#66717D', line: '#C7CED6', soft: '#E8EDF2', signal: '#D94B3D',
  gray: '#AEB8C2', pale: '#D9E4EC', white: '#FFFFFF',
});

export function normalizeSeries(data) {
  const divisor = data.value_scale === 'percent-points' ? 100 : 1;
  if (data.unit === '%' && !['percent-points', 'fraction'].includes(data.value_scale)) {
    throw new Error('Percent scale must be explicit');
  }
  return data.series.map(s => ({ id: s.id, name: s.name, values: s.values.map(v => {
    if (typeof v !== 'number' || !Number.isFinite(v)) throw new Error('Missing/non-finite chart value');
    return v / divisor;
  }) }));
}

export function renderData(panel) {
  const series = normalizeSeries(panel.data);
  // Horizontal native bars display category index zero at the bottom. Reverse
  // paired labels/values only in the disposable render projection so the visible
  // top-to-bottom order equals the canonical source order.
  const reversed = ['ranking','comparison','survey'].includes(panel.component_type);
  return {categories:reversed?[...panel.data.categories].reverse():[...panel.data.categories],
    series:series.map(s=>({...s,values:reversed?[...s.values].reverse():s.values}))};
}

export function chartConfig(panel, position, { fontFamily, compact = false, colors = palette } = {}) {
  if (!fontFamily) throw new Error('Choose a verified font family');
  const supported = ['ranking','comparison','column','line','stacked','survey'];
  if (!supported.includes(panel.component_type)) throw new Error(`Unsupported component: ${panel.component_type}`);
  const percent = panel.data.unit === '%';
  const decimals = panel.decimals ?? 0;
  if (!Number.isInteger(decimals) || decimals < 0 || decimals > 4) throw new Error('decimals must be 0–4');
  const format = `0${decimals ? '.' + '0'.repeat(decimals) : ''}${percent ? '%' : ''}`;
  const stacked = ['stacked','survey'].includes(panel.component_type);
  const line = panel.component_type === 'line';
  const horizontal = ['ranking','comparison','survey'].includes(panel.component_type);
  const fills = panel.component_type === 'survey'
    ? (panel.data.series.length > 4 ? [colors.muted,colors.gray,colors.pale,colors.sky,colors.blue,colors.navy,colors.signal] : [colors.pale,colors.sky,colors.blue,colors.navy])
    : [colors.navy, colors.blue, colors.sky, colors.gray, colors.pale, colors.muted, colors.signal];
  const textStyle = { typeface: fontFamily, fontSize: compact ? 14 : 18, fill: colors.muted };
  const allValues = normalizeSeries(panel.data).flatMap(s => s.values);
  const autoMin = Math.min(0, ...allValues);
  let autoMax = Math.max(0, ...allValues);
  if (stacked) autoMax = Math.max(...panel.data.categories.map((_,i) => normalizeSeries(panel.data).reduce((sum,s) => sum+s.values[i],0)));
  if (autoMax === autoMin) autoMax = autoMin + 1;
  const minimum = panel.axis_min ?? autoMin;
  const maximum = panel.axis_max ?? (percent ? Math.max(1, autoMax * (stacked ? 1 : 1.1)) : autoMax * 1.15);
  if (!(Number.isFinite(minimum) && Number.isFinite(maximum) && minimum < maximum)) throw new Error('Invalid chart scale');
  if (panel.axis_major_unit != null && !(Number.isFinite(panel.axis_major_unit) && panel.axis_major_unit > 0)) throw new Error('Invalid axis major unit');
  if (allValues.some(v => v < minimum || v > maximum)) throw new Error('Axis range would clip source values');
  const projected = renderData(panel);
  const series = projected.series.map((s, index) => {
    const fill = s.id === panel.focus_series ? colors.signal : fills[index % fills.length];
    const overrides = s.values.map((value, idx) => ({
      idx, showValue: line ? idx === s.values.length - 1 : (!stacked || Math.abs(value) >= (percent ? .065 : autoMax * .065)),
      position: stacked ? 'center' : 'outEnd',
      textStyle:{typeface:fontFamily,fontSize:compact?14:18,fill:stacked && ![colors.sky,colors.gray,colors.pale,colors.soft].includes(fill)?colors.white:colors.ink},
    }));
    return {
      name: s.name, values: s.values, valuesFormatCode: format, fill,
      line: { fill: line ? fill : 'none', width: line ? 3 : 0, style: 'solid' },
      ...(line ? {marker:{symbol:'circle',size:compact ? 4 : 6}} : {}),
      ...(!stacked && !line && panel.focus_categories?.length ? {
        points: projected.categories.map((name, idx) => ({idx,fill:panel.focus_categories.includes(name) ? colors.signal : fill})),
      } : {}),
      dataLabelOverrides: overrides,
    };
  });
  // A survey is an ordinary stack of original fractions. percentStacked would
  // silently normalize rounded 99%/101% totals, so it is intentionally not used.
  const valueAxis = {
    visible:true, min:minimum, max:maximum, numberFormatCode:format, textStyle,
    ...(panel.axis_major_unit != null ? {majorUnit:panel.axis_major_unit} : percent && minimum === 0 && maximum === 1 ? {majorUnit:.2} : {}),
    line:{fill:'none',width:0}, majorGridlines:{fill:colors.soft,width:1,style:'solid'},
  };
  const categoryAxis = {visible:true,textStyle,line:{fill:colors.line,width:1,style:'solid'},majorGridlines:null};
  return {
    type: line ? 'line' : 'bar',
    config: {
      position, categories:projected.categories, series,
      hasLegend:series.length > 1,
      legend:{position:'bottom',overlay:false,textStyle:{...textStyle,fontSize:compact ? 13 : 16}},
      ...(line ? {lineOptions:{smooth:false}} : {barOptions:{direction:horizontal?'bar':'column',grouping:stacked?'stacked':'clustered',gapWidth:horizontal?55:75,overlap:stacked?100:0}}),
      // Artifact Tool's axes are logical category (x) and value (y), even for bars.
      xAxis:categoryAxis, yAxis:valueAxis,
      dataLabels:{showValue:!line,position:stacked?'center':'outEnd',textStyle:{...textStyle,fill:stacked?colors.white:colors.ink,bold:false}},
      chartFill:colors.white,chartLine:{fill:'none',width:0},plotAreaFill:colors.white,plotAreaLine:{fill:'none',width:0},
    },
  };
}

function text(slide, value, box, size, color, family, bold = false) {
  const shape = slide.shapes.add({geometry:'textbox',position:box,fill:'none',line:{fill:'none',width:0}});
  shape.text = value;
  shape.text.style = {typeface:family,fontSize:size,color,bold,autoFit:'none'};
  return shape;
}

export function panelPositions(count, variant = 'wide') {
  if (count === 1) return [{left:64,top:208,width:variant === 'rail'?830:1152,height:388}];
  if (count === 2) return [{left:64,top:208,width:552,height:358},{left:664,top:208,width:552,height:358}];
  if (count === 3) return Array.from({length:3},(_,i) => ({left:64+i*396,top:218,width:360,height:330}));
  if (count < 3 || count > 6) throw new Error('Expected 1–6 panels');
  return Array.from({length:count},(_,i) => ({left:64+(i%3)*396,top:218+Math.floor(i/3)*208,width:360,height:168}));
}

export function addExhibitSlide(presentation, spec, { fontFamily, pageNumber = 1, colors = palette } = {}) {
  if (!fontFamily) throw new Error('fontFamily is required');
  if (!spec.panels?.length) throw new Error('No native exhibit panels');
  const slide = presentation.slides.add();
  slide.background.fill = colors.white;
  text(slide,spec.action_title,{left:64,top:42,width:1152,height:90},36,colors.ink,fontFamily,true);
  if (spec.subtitle) text(slide,spec.subtitle,{left:64,top:139,width:1152,height:34},18,colors.muted,fontFamily);
  const boxes = panelPositions(spec.panels.length,spec.variant);
  const contracts = [];
  spec.panels.forEach((panel,i) => {
    const box = boxes[i];
    const compact = spec.panels.length > 2;
    text(slide,`${panel.label || panel.data.series[0].name}，${panel.data.unit}`,
      {left:box.left,top:box.top-32,width:box.width,height:28},compact?16:18,colors.ink,fontFamily,true);
    const {type,config} = chartConfig(panel,box,{fontFamily,compact,colors});
    slide.charts.add(type,config);
    const projected=renderData(panel);
    contracts.push({chart_id:panel.chart_id,chart_order:i+1,categories:projected.categories,
      series:projected.series.map(({name,values}) => ({name,values})),
      number_format:panel.data.unit === '%' ? config.yAxis.numberFormatCode : null,
      require_workbook:true});
  });
  if (spec.implication) {
    const box = spec.variant === 'rail' && spec.panels.length === 1
      ? {left:944,top:242,width:272,height:306}
      : {left:64,top:612,width:1152,height:54};
    text(slide,spec.implication,box,spec.variant==='rail'?23:21,colors.navy,fontFamily,true);
  }
  const source = [...new Set(spec.panels.map(p => p.source).filter(Boolean))].join('；');
  text(slide,`来源：${source}`,{left:64,top:681,width:1064,height:24},12,colors.muted,fontFamily);
  text(slide,String(pageNumber).padStart(2,'0'),{left:1168,top:681,width:48,height:24},12,colors.muted,fontFamily);
  slide.speakerNotes.textFrame.setText([
    spec.action_title, spec.implication,
    ...spec.panels.map(p => `${p.chart_id}: ${p.source}\n单位: ${p.data.unit}; 原始尺度: ${p.data.value_scale}\n${JSON.stringify(p.data)}`),
    '独立分析重构；与麦肯锡不存在官方关联。',
  ].filter(Boolean).join('\n\n'));
  return {slide,contract:{slide_id:spec.slide_id,slide_number:pageNumber,charts:contracts}};
}
