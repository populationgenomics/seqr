import React, { useCallback, useState } from 'react'
import PropTypes from 'prop-types'
import { capitalize, isBoolean, isEqual } from 'lodash'

import { Form, Table, Icon, List, Message } from 'semantic-ui-react'
import styled from 'styled-components'
import { ReadableText } from '../ui'
import TemplateFile from '../templates/TemplateFile'

const ScrollTable = styled.div`
  margin-top: 1rem;
  overflow-x: scroll;
  overflow-y: hidden;
`

const TemplateDirectoryLink = () => (
  <a
    href="https://drive.google.com/drive/folders/1iHYMDY8-RzfqvvyEdubOHOmGzbLGUSUk"
    target="_blank"
    rel="noreferrer"
  >
    here
  </a>
)

const renderCellContent = (value) => {
  if (Array.isArray(value)) {
    return value.length ? <List>{value.map(v => <List.Item>{v}</List.Item>)}</List> : '-'
  }
  if (isBoolean(value)) {
    return capitalize(value.toString())
  }
  return value == null ? '-' : value.toString()
}

const ERROR_LIST_STYLE = { width: 250 }

/**
 * @param {TemplateRow} row
 * @returns {JSX.Element}
 */
const renderRowErrorList = (row) => {
  if (row.valid) return null

  return (
    <List animated style={ERROR_LIST_STYLE}>
      {
        row.columns.map(({ data, definition }) => {
          if (data.valid) return null

          const errorList = data.errors.map(e => <List.Item>{e}</List.Item>)
          return (
            <List.Item>
              <div><b>{definition.key}</b></div>
              <List bulleted>{errorList}</List>
            </List.Item>
          )
        })
      }
    </List>
  )
}

const TemplateUpload = ({ project, parser, onFormChange }) => {
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState(/** @type {string[]|JSXElement[]} */ [])
  const [valid, setValid] = useState(true)
  const [rows, setRows] = useState(/** @type {TemplateRow[]} */ [])

  const parseFile = useCallback((event) => {
    if (event.target.files[0]) {
      if (!event.target.files[0].name.match(/\.(tsv|csv)$/)) {
        setErrors(['Please upload a TSV or CSV file.'])
        setValid(false)
        setRows([])
        return
      }

      setIsLoading(true)
      parser.parse(
        {
          file: event.target.files[0],
          onComplete: ((result) => {
            console.debug(result)

            setIsLoading(false)

            // Copy array before sorting since sort function has side effects and modifies the original array
            const columnMismatch = !isEqual([...result.header].sort(), parser.columns.map(c => c.key).sort())

            if (columnMismatch) {
              setErrors([
                (
                  <div>
                    <p>Template file should have the following header columns:</p>
                    <List bulleted>{parser.columns.map(c => <List.Item key={c.id}>{c.key}</List.Item>)}</List>
                    <p>However, your file contains the header columns:</p>
                    <List bulleted>{result.header.map(f => <List.Item key={f}>{f}</List.Item>)}</List>
                  </div>
                ),
              ])
              setValid(false)
              setRows([])

              return
            }

            setErrors(result.errors)
            setValid(result.valid)
            setRows(result.rows)
          }),
          onError: ((e) => {
            setErrors([e.message])
            setIsLoading(false)
            setValid(false)
            setRows([])
          }),
        },
      )
    }
  }, [parser, setIsLoading, setErrors, setRows, setValid])

  const renderTableBody = useCallback(() => {
    if (!valid && !rows.length) {
      return (
        <Table.Row>
          <Table.Cell singleLine>Data could not be loaded. See errors for help.</Table.Cell>
        </Table.Row>
      )
    }

    // Render rows if we have them even if the parsing result is not valid, so we can display the errors
    // to the user.
    if (rows.length) {
      return rows.map(row => (
        <Table.Row>
          <Table.Cell error={!row.valid}>
            {row.valid ? <Icon name="checkmark" color="green" /> : <Icon name="attention" color="red" />}
          </Table.Cell>
          <Table.Cell error={!row.valid}>
            {renderRowErrorList(row)}
          </Table.Cell>
          {
            row.columns.map(({ data, definition }) => (
              <Table.Cell error={!data.valid}>
                {renderCellContent(data.value)}
              </Table.Cell>
            ))
          }
        </Table.Row>
      ))
    }

    return (
      <Table.Row>
        <Table.Cell singleLine>No data to display</Table.Cell>
      </Table.Row>
    )
  }, [rows, valid, errors])

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

      {
        !valid ? (
          <Message
            error
            header="Invalid template file"
            list={errors}
          />
        ) : null
      }

      <ScrollTable>
        <Table celled sortable>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell id="status">Status</Table.HeaderCell>
              <Table.HeaderCell id="comments">Comments</Table.HeaderCell>
              {
                parser
                  .columns
                  .map(c => <Table.HeaderCell id={c.key}>{`${c.key}${c.required ? ' *' : ''}`}</Table.HeaderCell>)
              }
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {renderTableBody()}
          </Table.Body>
        </Table>
      </ScrollTable>
    </>
  )
}

TemplateUpload.propTypes = {
  project: PropTypes.object.isRequired,
  parser: PropTypes.instanceOf(TemplateFile).isRequired,
  onFormChange: PropTypes.func.isRequired,
}

TemplateUpload.defaultProps = {}

export default TemplateUpload
