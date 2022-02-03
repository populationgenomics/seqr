import * as Papa from 'papaparse'
import { isEqual } from 'lodash'
import TemplateRow from './TemplateRow'

/**
 * Papa-parse error array
 * @typedef {{type: string, code: string, message: string, row: number}[]} ParseErrorList
 */

/**
 * Papa-parse metadata
 * @typedef {
 *  {delimiter: string, linebreak: string, aborted: boolean, fields: ?string[], truncated: boolean}
*  } ParseMetadata
 */

/**
 * TemplateFile `parse` onComplete callback signature
 * @callback onComplete
 * @param {{ rows: TemplateRow[], valid: boolean, errors: string[], header: string[] }} result
 */

/**
 * TemplateFile `onError` onError callback signature
 * @callback onError
 * @param {Error} error
 */

class TemplateFile {

  /**
   * @param {TemplateColumn[]} columns
   */
  constructor(columns) {
    if (!Array.isArray(columns)) {
      throw new Error("Parameter 'columns' must be an array of TemplateColumn objects")
    }

    /**
     * @type {TemplateColumn[]}
     */
    this.columns = Array.from(columns)
  }

  /**
   * @param {File} file
   * @param {onComplete} onComplete
   * @param {onError} onError
   *
   * @returns {TemplateFile}
   */
  parse({ file, onComplete, onError }) {
    Papa.parse(
      file,
      {
        header: true,
        skipEmptyLines: true,
        /**
         * @param {{data: *[], errors: ParseErrorList, meta: ParseMetadata}} results
         */
        complete: (results) => {
          const errors = results.errors.map(e => `(Row ${e.row}) ${e.message}`)

          if (!isEqual(this.columns.map(c => c.key).sort(), [...(results.meta.fields || [])].sort())) {
            onComplete({
              rows: [],
              valid: false,
              errors: ['File contains invalid columns in header'],
              header: results.meta.fields || [],
            })
            return
          }

          if (errors.length > 0) {
            onComplete({ rows: [], valid: false, errors, header: results.meta.fields || [] })
          } else {
            const rows = results.data.map((row, index) => {
              const columns = this.columns.map(c => ({ data: c.parse(row), definition: c }))
              return new TemplateRow({ index, columns })
            })

            const valid = rows.reduce((isValid, row) => isValid && row.valid, true)
            const validationErrors = valid ? [] : ['Some rows contain invalid information']

            onComplete({
              rows,
              valid,
              errors: validationErrors,
              header: results.meta.fields || [],
            })
          }
        },
        /**
         * @param {Error} error
         */
        error: error => onError(error),
      },
    )
  }

}

export default TemplateFile
