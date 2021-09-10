/* eslint-disable */

import React, { useCallback, useState } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import { Breadcrumb, Button, Grid, GridColumn, GridRow } from 'semantic-ui-react'

import { loadCurrentProject, unloadProject } from '../reducers'
import { getProjectDetailsIsLoading, getCurrentProject } from '../selectors'


const OnboardingWizard = ({ project }) => {
  /*************************************************************************************************
   * State
   ************************************************************************************************/
  const [step, setStep] = useState(0)
  const [formData, setFormData] = useState({})

  /*************************************************************************************************
   * Lifecycle
   ************************************************************************************************/


  /*************************************************************************************************
   * Helpers
   ************************************************************************************************/
  const nextStep = useCallback(() => {
    console.log(step)
    setStep(Math.min(step + 1, getBreadcrumbSteps().length - 1))
  }, [step])

  const previousStep = useCallback(() => {
    console.log(step)
    setStep(Math.max(step - 1, 0))
  }, [step])

  const getBreadcrumbSteps = useCallback(() => {
    const steps = [
      { key: 0, content: 'Welcome', link: false },
      { key: 1, content: 'Family', link: false },
      { key: 2, content: 'Individuals', link: false },
      { key: 3, content: 'Samples', link: false },
      { key: 4, content: 'Confirmation', link: false }
    ]

    return steps.map(
      (s) => {
        return {...s, active: step === s.key }
      }
    )
  }, [step])


  const renderStep = useCallback(() => {
    let form = null
    switch (step) {
      case 0:
        form = <div>Welcome</div>
        break
      case 1:
        form = <div>Store</div>
        break
      case 2:
        form = <div>T-Shirt</div>
        break
      default:
        throw new Error(`Unknown wizard step '${step}'`)
    }

    return form
  }, [step, project, formData])


  /*************************************************************************************************
   * Render
   ************************************************************************************************/
  return (
    <>
      <Grid>
        <GridRow>
          <GridColumn>
            {renderStep()}
          </GridColumn>
        </GridRow>
        <GridRow textAlign="right">
          <GridColumn floated="right">
            <Button onClick={previousStep}>Back</Button>
            <Button onClick={nextStep}>Next</Button>
          </GridColumn>
        </GridRow>
        <GridRow centered>
          <Breadcrumb
            size="large"
            icon="right angle"
            sections={getBreadcrumbSteps()}
          />
        </GridRow>
      </Grid>

    </>
  )
}

OnboardingWizard.propTypes = {
  project: PropTypes.object.isRequired,
}

const mapDispatchToProps = {
  loadCurrentProject,
  unloadProject,
}

const mapStateToProps = state => ({
  project: getCurrentProject(state),
  loading: getProjectDetailsIsLoading(state),
})

export { OnboardingWizard as OnboadingWizardComponent }

export default connect(mapStateToProps, mapDispatchToProps)(OnboardingWizard)
