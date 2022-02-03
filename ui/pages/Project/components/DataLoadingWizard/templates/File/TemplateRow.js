class TemplateRow {

  /** @type {number} #index */
  #index

  /** @type {{data: {value: *, valid: boolean, errors: string[]}, definition: TemplateColumn }[]} #columns */
  #columns

  /** @type {boolean} #valid */
  #valid

  /**
   * @param {number} index Row number
   * @param {{data: {value: *, valid: boolean, errors: string[]}, definition: TemplateColumn }[]} columns
   */
  constructor({ index, columns }) {
    if (!Array.isArray(columns)) {
      throw new Error("Parameter 'columns' must be an array")
    }

    this.#index = index
    this.#columns = Array.from(columns)
    this.#valid = this.columns.map(column => column.data.valid).reduce((a, b) => a && b, true)
  }

  get index() { return this.#index }

  get columns() { return this.#columns }

  get valid() { return this.#valid }

}

export default TemplateRow
