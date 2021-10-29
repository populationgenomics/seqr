import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import { Error401 } from '../../../../shared/components/page/Errors'
import { getCurrentProject } from '../../selectors'

const OnboardingWizard = ({ match, project }) => {
  if (!project.canEdit) {
    return <Error401 />
  }

  return (
    <div>
      <h1>Hello, world!</h1>
      <pre>{JSON.stringify(match, null, 2)}</pre>
      <pre>{JSON.stringify(project, null, 2)}</pre>
    </div>
  )
}

OnboardingWizard.propTypes = {
  match: PropTypes.object,
  project: PropTypes.object,
}

const mapStateToProps = state => ({
  project: getCurrentProject(state),
})

export default connect(mapStateToProps)(OnboardingWizard)
