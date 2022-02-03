import * as _ from 'lodash'
import { INHERITANCE_MODE_OPTIONS, ONSET_AGE_OPTIONS } from '../../../../constants'

/**
 * @param {*[]} collection
 * @param {?string} message
 * @returns {string[]}
 */
export const validateUnique = (collection, message = null) => {
  const counts = _.countBy(collection)

  const errors = _.zip(collection, Object.values(counts)).map(([key, count]) => {
    if (count > 1) {
      return message || `'${key}' is not unique, and was counted ${count} times`
    }
    return null
  })

  return errors.filter(e => e != null)
}

/**
 * @param {?string} value
 * @param {?string} message
 * @returns {string|null}
 */
export const validateHpoTerm = (value, message = null) => {
  if (!value) return null

  if (!value.toString().toUpperCase().match(/HP:\d{7}/)) {
    return message || `'${value}' is not a valid HPO term`
  }
  return null
}

/**
 * @param {string[]} collection
 * @param {?string} message
 * @returns {string[]}
 */
export const validateHpoTerms = (collection, message = null) => (
  collection
    .map(v => validateHpoTerm(v, message))
    .filter(e => e != null)
)

/**
 * @param {?string} value
 * @param {?string} message
 * @returns {string|null}
 */
export const validateOnsetCategory = (value, message = null) => {
  if (!value) return null

  const categories = ONSET_AGE_OPTIONS.map(o => o.text)

  if (!categories.map(c => c.toLowerCase()).includes(value.toLowerCase())) {
    return message || `'${value}' is not one of ${categories.join(', ')}`
  }

  return null
}

/**
 * @param {?string} value
 * @param {?string} message
 * @returns {string|null}
 */
export const validateModeOfInheritanceTerm = (value, message = null) => {
  if (!value) return null

  const categories = INHERITANCE_MODE_OPTIONS.map(o => o.text)

  if (!categories.map(c => c.toLowerCase()).includes(value.toLowerCase())) {
    return message || `'${value}' is not one of ${categories.join(', ')}`
  }

  return null
}

/**
 * @param {string[]} collection
 * @param {?string} message
 * @returns {string[]}
 */
export const validateModeOfInheritanceTerms = (collection, message) => (
  collection
    .map(v => validateModeOfInheritanceTerm(v, message))
    .filter(e => e != null)
)

/**
 * @param {?string} value
 * @param {?string} message
 * @returns {string|null}
 */
export const validateOmimTerm = (value, message = null) => {
  if (!value) return null

  if (!value.toString().toUpperCase().match(/^OMIM:\d+$/)) {
    return message || `'${value}' is not a valid OMIM term`
  }
  return null
}

/**
 * @param {string[]} collection
 * @param {?string} message
 * @returns {string[]}
 */
export const validateOmimTerms = (collection, message) => (
  collection
    .map(v => validateOmimTerm(v, message))
    .filter(e => e != null)
)

export default {
  validateUnique,
  validateHpoTerm,
  validateHpoTerms,
  validateOnsetCategory,
  validateModeOfInheritanceTerm,
  validateModeOfInheritanceTerms,
  validateOmimTerm,
  validateOmimTerms,
}
