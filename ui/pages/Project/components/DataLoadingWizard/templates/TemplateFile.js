import * as Papa from 'papaparse'

class TemplateFile {

  /**
   * @param {TemplateColumn[]} columns
   */
  constructor(columns) {
    /**
     * @type {TemplateColumn[]}
     */
    this.columns = [...columns]

    /**
     * @type {{valid: boolean, columns: [TemplateColumn, {value: *, valid: boolean, errors: string[]}][]}[]}
     */
    this.rows = []

    /**
     * @type {?boolean}
     */
    this.valid = null

    /**
     * @type {{type: string, code: string, message: string, row: number}[]}
     */
    this.fileErrors = []

    /**
     * @type {{delimiter: string, linebreak: string, aborted: boolean, fields: ?string[], truncated: boolean}}
     */
    this.fileMetadata = {}
  }

  parse(file, onComplete, onError) {
    this.rows = []
    this.valid = null
    this.fileErrors = []
    this.fileMetadata = {}

    Papa.parse(
      file,
      {
        header: true,
        skipEmptyLines: true,
        complete: (results) => {
          this.fileMetadata = { ...results.meta }
          this.fileErrors = [...results.errors]

          if (this.fileErrors.length === 0) {
            this.rows = results.data.map((row) => {
              const columns = this.columns.map(c => [c, c.parse(row)])
              const valid = columns.reduce((acc, column) => acc && column[1].valid, true)

              return { valid, columns }
            })

            this.valid = this.rows.reduce((acc, row) => acc && row.valid, true)
          } else {
            this.valid = false
          }

          onComplete(results)
        },
        error: (e) => {
          this.valid = false
          this.fileErrors = [{ type: e.name, code: '500', message: e.message, row: -1 }]
          onError(e)
        },
      },
    )

    return this
  }

}

export default TemplateFile
