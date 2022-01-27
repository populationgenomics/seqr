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
   * @param {[]|{}} row
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

    const validationErrors = this.validators.map(validator => validator(result)).filter(e => e != null)

    return {
      value: result,
      errors: validationErrors,
      valid: validationErrors.length === 0,
    }
  }

}

export default TemplateColumn
