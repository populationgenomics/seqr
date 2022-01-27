import React, { useCallback, useState } from 'react'
import PropTypes from 'prop-types'

import { Form, Table, Icon, List, Message } from 'semantic-ui-react'
import { ReadableText } from '../ui'
import TemplateFile from '../templates/TemplateFile'
import FamilyTemplateColumns from '../templates/Family'

const TemplateDirectoryLink = () => (
  <a
    href="https://drive.google.com/drive/folders/1iHYMDY8-RzfqvvyEdubOHOmGzbLGUSUk"
    target="_blank"
    rel="noreferrer"
  >
    here
  </a>
)

const FamilyMetadataUpload = ({ project, onFormChange }) => {
  const columns = FamilyTemplateColumns()

  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [rows, setRows] = useState([])
  const [valid, setValid] = useState(null)

  const parseFile = useCallback((event) => {
    if (event.target.files[0]) {
      setError(null)
      setValid(null)
      setRows([])

      if (!event.target.files[0].name.match(/\.(tsv|csv)$/)) {
        setError('Please upload a TSV or CSV file.')
        setValid(false)
        return
      }

      setIsLoading(true)
      const parser = new TemplateFile(columns)
      parser.parse(
        event.target.files[0],
        () => {
          setError(null)
          setIsLoading(false)
          setValid(parser.valid)
          setRows([...parser.rows])

          console.debug(parser)
        },
        (e) => {
          setError(e)
          setIsLoading(false)
          setValid(false)
          setRows([])
        },
      )
    }
  }, [setIsLoading, setError, setRows])

  return (
    <>
      <ReadableText>
        In this section, you will provide all information relating to the families in your project. Please download
        the families template from
        {' '}
        <TemplateDirectoryLink />
        { '. ' }
        Once you have filled in this template, upload it via this step and correct any validation errors
        before proceeding.
      </ReadableText>

      <Form loading={isLoading}>
        <Form.Input type="file" label="Family Template" onChange={parseFile} />
      </Form>

      {valid === false ? (
        <Message
          error
          header="The file you have uploaded contains errors. Please address these errors before proceeding."
        />
      ) : null}

      <Table celled>
        <Table.Header>
          <Table.Row>
            <Table.HeaderCell />
            {columns.map(c => <Table.HeaderCell key={c.key}>{`${c.key}${c.required ? ' *' : ''}`}</Table.HeaderCell>)}
            <Table.HeaderCell>Comments</Table.HeaderCell>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {error ?
            (
              <Table.Row>
                <Table.Cell singleLine>{error ? error.toString() : 'No data loaded'}</Table.Cell>
              </Table.Row>
            ) :
            rows.map(row => (
              <Table.Row>
                <Table.Cell>
                  {row.valid ? <Icon name="checkmark" color="green" /> : <Icon name="attention" color="red" />}
                </Table.Cell>
                {row.columns.map(([columnDef, columnValue]) => (
                  <Table.Cell id={columnDef.id} error={!columnValue.valid}>
                    {Array.isArray(columnValue.value) ? columnValue.value.join(', ') : columnValue.value}
                  </Table.Cell>
                ))}
                <Table.Cell error={!row.valid}>
                  {row.valid ? null : (
                    <List bulleted>
                      {
                        row.columns.map(([columnDef, columnValue]) => {
                          if (columnValue.valid) return null

                          const innerList = columnValue.errors.map((e, i) => (
                            <List.Item key={`${columnDef.id}-error-list-item-${i + 1}`}>{e}</List.Item>
                          ))
                          return (
                            <List.Item key={`${columnDef.id}-error-list`}>
                              <div>{columnDef.key}</div>
                              <List bulleted>{innerList}</List>
                            </List.Item>
                          )
                        })
                      }
                    </List>
                  )}
                </Table.Cell>
              </Table.Row>
            )) }
        </Table.Body>
      </Table>
    </>
  )
}

FamilyMetadataUpload.propTypes = {
  project: PropTypes.object.isRequired,
  onFormChange: PropTypes.func.isRequired,
}

FamilyMetadataUpload.defaultProps = {}

export default FamilyMetadataUpload
