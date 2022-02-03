import TemplateColumn from './File/TemplateColumn'
import { parseString, parseStringArray, parseBoolean, parseYear } from './utils/parsers'
import { validateHpoTerms, validateModeOfInheritanceTerms, validateOmimTerms, validateOnsetCategory } from './utils/validators'

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
    id: 'hpoTermsPresent',
    key: 'HPO Terms (present)',
    index: 2,
    required: false,
    parser: parseStringArray,
    validators: [validateHpoTerms],
  }),
  new TemplateColumn({
    id: 'hpoTermsAbsent',
    key: 'HPO Terms (absent)',
    index: 3,
    required: false,
    parser: parseStringArray,
    validators: [validateHpoTerms],
  }),
  new TemplateColumn({
    id: 'birthYear',
    key: 'Birth Year',
    index: 4,
    required: false,
    parser: parseYear,
    validators: [],
  }),
  new TemplateColumn({
    id: 'deathYear',
    key: 'Death Year',
    index: 5,
    required: false,
    parser: parseYear,
    validators: [],
  }),
  new TemplateColumn({
    id: 'ageOfOnset',
    key: 'Age of Onset',
    index: 6,
    required: false,
    parser: parseString,
    validators: [validateOnsetCategory],
  }),
  new TemplateColumn({
    id: 'individualNotes',
    key: 'Individual Notes',
    index: 7,
    required: false,
    parser: parseString,
    validators: [],
  }),
  new TemplateColumn({
    id: 'consanguinity',
    key: 'Consanguinity',
    index: 8,
    required: false,
    parser: parseBoolean,
    validators: [],
  }),
  new TemplateColumn({
    id: 'otherAffectedRelatives',
    key: 'Other Affected Relatives',
    index: 9,
    required: false,
    parser: parseBoolean,
    validators: [],
  }),
  new TemplateColumn({
    id: 'expectedInheritanceMode',
    key: 'Expected Mode of Inheritance',
    index: 10,
    required: false,
    parser: parseStringArray,
    validators: [validateModeOfInheritanceTerms],
  }),
  new TemplateColumn({
    id: 'fertilityMedications',
    key: 'Fertility medications',
    index: 11,
    required: false,
    parser: parseBoolean,
    validators: [],
  }),
  new TemplateColumn({
    id: 'intrauterineInsemination',
    key: 'Intrauterine insemination',
    index: 12,
    required: false,
    parser: parseBoolean,
    validators: [],
  }),
  new TemplateColumn({
    id: 'inVitroFertilization',
    key: 'In vitro fertilization',
    index: 13,
    required: false,
    parser: parseBoolean,
    validators: [],
  }),
  new TemplateColumn({
    id: 'intraCytoplasmicSpermInjection',
    key: 'Intra-cytoplasmic sperm injection',
    index: 14,
    required: false,
    parser: parseBoolean,
    validators: [],
  }),
  new TemplateColumn({
    id: 'gestationalSurrogacy',
    key: 'Gestational surrogacy',
    index: 15,
    required: false,
    parser: parseBoolean,
    validators: [],
  }),
  new TemplateColumn({
    id: 'donorEgg',
    key: 'Donor egg',
    index: 16,
    required: false,
    parser: parseBoolean,
    validators: [],
  }),
  new TemplateColumn({
    id: 'donorSperm',
    key: 'Donor sperm',
    index: 17,
    required: false,
    parser: parseBoolean,
    validators: [],
  }),
  new TemplateColumn({
    id: 'maternalAncestry',
    key: 'Maternal Ancestry',
    index: 18,
    required: false,
    parser: parseStringArray,
    validators: [],
  }),
  new TemplateColumn({
    id: 'paternalAncestry',
    key: 'Paternal Ancestry',
    index: 19,
    required: false,
    parser: parseStringArray,
    validators: [],
  }),
  new TemplateColumn({
    id: 'preDiscoveryOmimDisorders',
    key: 'Pre-discovery OMIM disorders',
    index: 20,
    required: false,
    parser: parseStringArray,
    validators: [validateOmimTerms],
  }),
  new TemplateColumn({
    id: 'previouslyTestedGenes',
    key: 'Previously Tested Genes',
    index: 21,
    required: false,
    parser: parseStringArray,
    validators: [],
  }),
  new TemplateColumn({
    id: 'candidateGenes',
    key: 'Candidate Genes',
    index: 22,
    required: false,
    parser: parseStringArray,
    validators: [],
  }),
])

export default IndividualTemplateColumns
