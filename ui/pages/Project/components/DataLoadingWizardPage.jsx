import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import { Error401 } from '../../../shared/components/page/Errors'
import { getCurrentProject } from '../selectors'

import DataLoadingWizardForm from './DataLoadingWizardForm/DataLoadingWizardForm'

const DataLoadingWizardPage = ({ project }) => {
  if (!project.canEdit) {
    return <Error401 />
  }

  return <DataLoadingWizardForm project={project} />
}

DataLoadingWizardPage.propTypes = {
  project: PropTypes.object,
}

const mapStateToProps = state => ({
  project: getCurrentProject(state),
})

export default connect(mapStateToProps)(DataLoadingWizardPage)
