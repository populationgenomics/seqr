import TemplateColumn from './TemplateColumn'
import { parseString } from './parsers'

const IndividualTemplateColumns = () => ([
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
    id: 'individualId',
    key: 'Individual ID',
    index: 1,
    required: true,
    parser: parseString,
    validators: [
      v => ((!v) ? 'An individual ID must be present.' : null),
    ],
  }),
  new TemplateColumn({
    id: 'paternalId',
    key: 'Paternal ID',
    index: 2,
    required: false,
    parser: parseString,
    validators: [],
  }),
  new TemplateColumn({
    id: 'maternalId',
    key: 'Maternal ID',
    index: 3,
    required: false,
    parser: parseString,
    validators: [],
  }),
  new TemplateColumn({
    id: 'sex',
    key: 'Sex',
    index: 4,
    required: true,
    parser: parseString,
    validators: [
      (v) => {
        if (!v) {
          return (
            'A character representing sex must be present. ' +
            "The character '1' represents male, '2' represents female, " +
            "and any other character besides '1' and '2' represents unknown."
          )
        }
        return null
      },
    ],
  }),
  new TemplateColumn({
    id: 'affectedStatus',
    key: 'Affected Status',
    index: 5,
    required: true,
    parser: parseString,
    validators: [
      (v) => {
        if (!v) {
          return (
            'A character representing phenotype affect status must be present. ' +
            "The characters '0' and '-9' represent missing, '1' represents unaffected and '2' represents affected. " +
            'Any other characters are interpreted as string phenotype values.'
          )
        }
        return null
      },
    ],
  }),
  new TemplateColumn({
    id: 'notes',
    key: 'Notes',
    index: 6,
    required: false,
    parser: parseString,
    validators: [],
  }),
])

export default IndividualTemplateColumns
