import test from 'node:test';
import assert from 'node:assert/strict';
import {chartConfig, normalizeSeries, panelPositions,renderData} from '../scripts/native_exhibits.mjs';

const panel={component_type:'survey',data:{unit:'%',value_scale:'percent-points',categories:['A','B'],series:[{id:'yes',name:'改善',values:[32,70]},{id:'no',name:'其他',values:[67,30]}]}};
test('original percentage points become fractions without normalizing 99% totals',()=>{
  assert.deepEqual(normalizeSeries(panel.data)[0].values,[.32,.7]);
  const {config}=chartConfig(panel,{left:0,top:0,width:800,height:400},{fontFamily:'Arial'});
  assert.equal(config.barOptions.grouping,'stacked');
  assert.equal(config.series[1].values[1],.67);
  assert.equal(config.yAxis.numberFormatCode,'0%');
  assert.equal(config.yAxis.majorUnit,.2);
});
test('negative values retained in native ranking data and axis',()=>{
  const p={component_type:'ranking',data:{unit:'亿元',value_scale:'raw',categories:['A','B'],series:[{id:'s',name:'利润变化',values:[-17,12]}]}};
  const {config}=chartConfig(p,{}, {fontFamily:'Arial'});
  assert.deepEqual(config.series[0].values,[12,-17]);
  assert.equal(config.yAxis.min,-17);
});
test('bar projection reverses paired categories and values, not canonical content',()=>{
  assert.deepEqual(renderData(panel).categories,['B','A']);
  assert.deepEqual(renderData(panel).series[0].values,[.7,.32]);
  assert.deepEqual(panel.data.categories,['A','B']);
});
test('axis clipping and missing data fail, not hidden or zero-filled',()=>{
  assert.throws(()=>chartConfig({...panel,axis_max:.5},{},{fontFamily:'Arial'}),/clip/);
  assert.throws(()=>normalizeSeries({...panel.data,series:[{name:'s',values:[null]}]}));
  assert.throws(()=>chartConfig({...panel,axis_major_unit:-.2},{},{fontFamily:'Arial'}),/major/);
});
test('rail and wide change geometry, not source facts',()=>{
  assert.notDeepEqual(panelPositions(1,'rail'),panelPositions(1,'wide'));
  const a=chartConfig(panel,panelPositions(1,'rail')[0],{fontFamily:'Arial'});
  const b=chartConfig(panel,panelPositions(1,'wide')[0],{fontFamily:'Arial'});
  assert.deepEqual(a.config.series,b.config.series);
});
test('three small multiples use the available single-row height',()=>{
  const boxes=panelPositions(3);
  assert.equal(new Set(boxes.map(b=>b.top)).size,1);
  assert.ok(boxes.every(b=>b.height>=300 && b.top+b.height<600));
  assert.ok(boxes.every((b,i)=>i===0 || boxes[i-1].left+boxes[i-1].width<b.left));
});
test('all six primitives create native bar/line configs',()=>{
  for(const type of ['ranking','comparison','column','line','stacked','survey']) {
    const {type:chartType,config}=chartConfig({...panel,component_type:type},{},{fontFamily:'Arial'});
    assert.ok(['bar','line'].includes(chartType));
    assert.ok(config.series.length>0);
    assert.equal(config.xAxis.textStyle.typeface,'Arial');
  }
});
