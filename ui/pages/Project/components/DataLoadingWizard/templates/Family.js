import TemplateColumn from './TemplateColumn'
import { parseString, parseStringArray } from './parsers'

const FamilyTemplateColumns = () => ([
  new TemplateColumn({
    id: 'familyId',
    key: 'Family ID',
    index: 0,
    required: true,
    parser: parseString,
    validators: [
      v => ((!v) ? 'A family ID must be present.' : null),
    ],
  }),
  new TemplateColumn({
    id: 'displayName',
    key: 'Display Name',
    index: 1,
    required: false,
    parser: parseString,
    validators: [],
  }),
  new TemplateColumn({
    id: 'description',
    key: 'Description',
    index: 2,
    required: false,
    parser: parseString,
    validators: [],
  }),
  new TemplateColumn({
    id: 'codedPhenotype',
    key: 'Coded Phenotype',
    index: 3,
    required: false,
    parser: parseStringArray,
    validators: [],
  }),
])

export default FamilyTemplateColumns
