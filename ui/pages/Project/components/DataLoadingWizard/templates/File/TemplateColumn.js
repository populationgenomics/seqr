class TemplateColumn {

  constructor({ id, key, index, required = false, parser = x => x, validators = [] }) {
    this.id = id
    this.key = key
    this.index = index
    this.required = required || false
    this.parser = parser || (x => x)
    this.validators = validators || []
  }

  /**
   * @param {*[]|{}} row
   * @returns {{value: *, valid: boolean, errors: string[]}}
   */
  parse(row) {
    let result = null
    if (Array.isArray(row)) {
      result = this.parser(row[this.index])
    } else if (row.constructor.name === 'Object') {
      result = this.parser(row[this.key])
    } else {
      throw new Error(
        `TemplateColumn 'parse' function expects an Array or an Object, but received ${row.constructor.name}`,
      )
    }

    // Some validators may return a list of errors if they validate a field which is parsed into an array, for example
    // a comma-delimited list of string values. Use flatMap to flatten all validation errors into a single array.
    const validationErrors = this.validators.flatMap(validator => validator(result)).filter(e => e != null)

    return {
      value: result,
      errors: validationErrors,
      valid: validationErrors.length === 0,
    }
  }

}

export default TemplateColumn
