import React from 'react'
import PropTypes from 'prop-types'

import { extent } from 'd3-array'
import { axisBottom, axisLeft } from 'd3-axis'
import { scaleLinear, scaleLog } from 'd3-scale'
import { select } from 'd3-selection'

const GRAPH_HEIGHT = 400
const GRAPH_WIDTH = 600
const GRAPH_MARGIN = { top: 10, bottom: 40, right: 30, left: 45 }

class RnaSeqOutliersVolcanoPlot extends React.PureComponent {

  static propTypes = {
    data: PropTypes.object,
    genesById: PropTypes.object,
  }

  componentDidMount() {
    const { data, genesById } = this.props
    const dataArray = Object.values(data)

    const svg = select(this.svg).append('g')
      .attr('transform', `translate(${GRAPH_MARGIN.left},${GRAPH_MARGIN.top})`)

    const x = scaleLinear().domain(extent(dataArray.map(d => d.zScore))).range([0, GRAPH_WIDTH])
    const y = scaleLog().domain(extent(dataArray.map(d => d.pValue))).range([0, GRAPH_HEIGHT])
    const r = scaleLinear().domain(extent(dataArray.map(d => d.deltaPsi))).range([1, 10])

    // x-axis
    svg.append('g')
      .attr('transform', `translate(0,${GRAPH_HEIGHT + 5})`)
      .call(axisBottom(x).tickSizeOuter(0))

    // y-axis
    svg.append('g')
      .attr('transform', 'translate(-10,0)')
      .call(axisLeft(y).tickSizeOuter(0).ticks(5, val => -Math.log10(val)))

    // x-axis label
    svg.append('text')
      .attr('text-anchor', 'end')
      .attr('y', GRAPH_HEIGHT + GRAPH_MARGIN.bottom)
      .attr('x', GRAPH_WIDTH / 2)
      .text('Z-score')

    // y-axis label
    svg.append('text')
      .attr('text-anchor', 'end')
      .attr('transform', 'rotate(-90)')
      .attr('y', 10 - GRAPH_MARGIN.left)
      .attr('x', GRAPH_MARGIN.bottom - (GRAPH_HEIGHT / 2))
      .text('-log(P-value)')

    // scatterplot
    const dataPoints = svg.append('g').selectAll('dot').data(dataArray).enter()
      .append('g')

    dataPoints.append('circle')
      .attr('cx', d => x(d.zScore))
      .attr('cy', d => y(d.pValue))
      .attr('r', d => (d.deltaPsi ? r(d.deltaPsi) : 3))
      .style('fill', 'None')
      .style('stroke', d => (d.isSignificant ? 'red' : 'lightgrey'))

    dataPoints.append('text')
      .text(d => (d.isSignificant ? (genesById[d.geneId] || {}).geneSymbol : null))
      .attr('text-anchor', d => (x(d.zScore) > GRAPH_WIDTH - 100 ? 'end' : 'start'))
      .attr('x', (d) => {
        const xPos = x(d.zScore)
        return xPos + (5 * (xPos > GRAPH_WIDTH - 100 ? -1 : 1))
      })
      .attr('y', d => y(d.pValue))
      .style('fill', 'red')
      .style('font-weight', 'bold')
  }

  setSvgElement = (element) => {
    this.svg = element
  }

  render() {
    return (
      <svg
        ref={this.setSvgElement}
        width={GRAPH_WIDTH + GRAPH_MARGIN.left + GRAPH_MARGIN.right}
        height={GRAPH_HEIGHT + GRAPH_MARGIN.top + GRAPH_MARGIN.bottom}
      />
    )
  }

}

export default RnaSeqOutliersVolcanoPlot
