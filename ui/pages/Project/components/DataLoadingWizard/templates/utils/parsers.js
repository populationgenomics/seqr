/**
 * @param {?string} value
 * @returns {string|null}
 */
export const parseString = (value) => {
  if (value?.toString()?.trim()) {
    return value.toString().trim()
  }
  return null
}

/**
 * @param {?string} value
 * @param {string} separator
 * @returns {string[]}
 */
export const parseStringArray = (value, separator = ',') => {
  if (!value) return []

  if (value.toString().trim()) {
    return Array.from(
      new Set(
        value
          .toString()
          .trim()
          .split(separator)
          .map(p => p?.trim() || null)
          .filter(p => p?.trim() && p.trim().length > 0),
      ),
    )
  }
  return []
}

/**
 * @param {?string} value
 * @returns {number|null}
 */
export const parseNumber = (value) => {
  const n = Number(value?.toString()?.trim())
  if (Number.isFinite(n)) {
    return n
  }
  return null
}

/**
 * @param {?string} value
 * @returns {boolean|null}
 */
export const parseBoolean = (value) => {
  const b = value?.toString()?.trim()?.toLowerCase()
  if (value) {
    switch (b) {
      case 'true': return true
      case 'false': return false
      default: return null
    }
  }
  return null
}

/**
 * @param {?string} value
 * @returns {string|null}
 */
export const parseYear = (value) => {
  const d = value?.toString()?.trim()
  const match = d.match(/(?<year>\d{4})/)

  if (match?.groups?.year) {
    return match.groups.year
  }
  return null
}

export default {
  parseString,
  parseStringArray,
  parseNumber,
  parseBoolean,
  parseYear,
}
