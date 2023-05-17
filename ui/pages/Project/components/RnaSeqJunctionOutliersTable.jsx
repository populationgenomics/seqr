import React from 'react'
import PropTypes from 'prop-types'

import { RNASEQ_JUNCTION_PADDING } from 'shared/utils/constants'
import { camelcaseToTitlecase } from 'shared/utils/stringUtils'
import { GeneSearchLink } from 'shared/components/buttons/SearchResultsLink'
import DataTable from 'shared/components/table/DataTable'
import FamilyReads from 'shared/components/panel/family/FamilyReads'
import { COVERAGE_TYPE, JUNCTION_TYPE } from 'shared/components/panel/family/constants'
import ShowGeneModal from 'shared/components/buttons/ShowGeneModal'
import { ButtonLink } from 'shared/components/StyledComponents'
import { getLocus } from 'shared/components/panel/variants/VariantUtils'

const RNA_SEQ_SPLICE_NUM_FIELDS = ['zScore', 'pValue', 'deltaPsi']
const RNA_SEQ_SPLICE_DETAIL_FIELDS = ['type', 'readCount', 'rareDiseaseSamplesWithJunction', 'rareDiseaseSamplesTotal']

const RNA_SEQ_SPLICE_COLUMNS = [
  {
    name: 'junctionLocus',
    content: 'Junction',
    width: 4,
    format: (row, isExport, { onClickCell, familyGuid }) => (
      <div>
        <ButtonLink onClick={onClickCell(row)}>
          {row.junctionLocus}
        </ButtonLink>
        <GeneSearchLink
          buttonText=""
          icon="search"
          location={`${row.chrom}:${Math.max(1, row.start - RNASEQ_JUNCTION_PADDING)}-${row.end + RNASEQ_JUNCTION_PADDING}`}
          familyGuid={familyGuid}
        />
      </div>
    ),
  }, {
    name: 'gene',
    content: 'Gene',
    width: 2,
    format: (row, isExport, { familyGuid }) => (
      <div>
        <ShowGeneModal gene={row} />
        <GeneSearchLink
          buttonText=""
          icon="search"
          location={row.geneId}
          familyGuid={familyGuid}
          floated="right"
        />
      </div>
    ),
  },
  ...RNA_SEQ_SPLICE_NUM_FIELDS.map(name => (
    {
      name,
      content: camelcaseToTitlecase(name).replace(' ', '-'),
      format: row => row[name].toPrecision(3),
    }
  )),
  ...RNA_SEQ_SPLICE_DETAIL_FIELDS.map(name => (
    {
      name,
      content: camelcaseToTitlecase(name).replace(' ', '-'),
    }
  )),
]

class RnaSeqJunctionOutliersTable extends React.PureComponent {

  static propTypes = {
    reads: PropTypes.object,
    updateReads: PropTypes.func,
    data: PropTypes.arrayOf(PropTypes.object),
    familyGuid: PropTypes.string,
    tissueType: PropTypes.string,
  }

  openReads = row => () => {
    const { updateReads, familyGuid, tissueType } = this.props
    const { chrom, start, end } = row
    updateReads(familyGuid, getLocus(chrom, start, RNASEQ_JUNCTION_PADDING, end - start),
      [JUNCTION_TYPE, COVERAGE_TYPE], tissueType)
  }

  render() {
    const { data, reads, familyGuid } = this.props

    // eslint-disable-next-line react-perf/jsx-no-new-object-as-prop
    const formatProps = { onClickCell: this.openReads, familyGuid }

    return (
      <div>
        {reads}
        <DataTable
          data={data}
          idField="idField"
          columns={RNA_SEQ_SPLICE_COLUMNS}
          defaultSortColumn="pValue"
          maxHeight="600px"
          formatProps={formatProps}
        />
      </div>
    )
  }

}

export default props => <FamilyReads layout={RnaSeqJunctionOutliersTable} noTriggerButton {...props} />
