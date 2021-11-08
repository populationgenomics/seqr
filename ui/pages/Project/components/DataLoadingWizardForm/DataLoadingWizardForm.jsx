import React, { useState, useEffect, useCallback } from 'react'
import PropTypes from 'prop-types'
import { Breadcrumb } from 'semantic-ui-react'

import { Centered, FormSection, FormStepButtons } from './ui'
import { Welcome, FamilyMetadataUpload } from './steps'
import { Error404 } from '../../../../shared/components/page/Errors'

const BREADCRUMBS = [
  { key: 0, content: 'Welcome', link: true, active: true },
  { key: 1, content: 'Family metadata', link: true, active: false },
  { key: 2, content: 'Individual metadata', link: true, active: false },
  { key: 3, content: 'Sample mapping', link: true, active: false },
  { key: 4, content: 'Review', link: true, active: false },
]


const DataLoadingWizardForm = ({ project }) => {
  // ---- Debug ---- //
  console.group('Project Object')
  console.log(project)
  console.groupEnd()

  // ---- State ----- //
  const [breadCrumbs, setBreadcrumbs] = useState(BREADCRUMBS.map((b) => { return { ...b } }))
  const [activeFormStepIndex, setActiveFormStepIndex] = useState(0)
  const [formSteps, setFormSteps] = useState(BREADCRUMBS.map(
    (_, index) => {
      return { formData: {}, isComplete: (index === 0) }
    },
  ))

  // ---- Callbacks ----- //
  const updateFormStep = useCallback((stepNumber, { formData, isComplete }) => {
    setFormSteps(formSteps.map(
      (step, index) => {
        if (stepNumber === index) {
          return { formData, isComplete }
        }
        return { ...step }
      },
    ))
  }, [])

  const enableReview = useCallback(() => {
    return formSteps
      .slice(0, formSteps.length - 1)
      .reduce((acc, step) => acc && step.isComplete, true)
  }, [formSteps])

  const enableNext = useCallback(() => {
    if (activeFormStepIndex === (formSteps.length - 2)) {
      return enableReview()
    }

    return activeFormStepIndex < formSteps.length
  }, [formSteps, activeFormStepIndex, enableReview])

  const getFormStepComponent = useCallback(() => {
    switch (activeFormStepIndex) {
      case 0:
        return <Welcome />
      case 1:
        return <FamilyMetadataUpload
          project={project}
          onFormChange={({ formData, isComplete }) => updateFormStep(1, { formData, isComplete })}
        />
      case 2:
        return <div>{ breadCrumbs[activeFormStepIndex].content }</div>
      case 3:
        return <div>{ breadCrumbs[activeFormStepIndex].content }</div>
      case 4:
        return <div>{ breadCrumbs[activeFormStepIndex].content }</div>
      case 5:
        return <div>{ breadCrumbs[activeFormStepIndex].content }</div>
      default:
        return <Error404 />
    }
  }, [project, activeFormStepIndex, updateFormStep])


  // ---- Effects ---- //
  useEffect(() => {
    setBreadcrumbs(breadCrumbs.map((b, index) => {
      return { ...b, active: (index === activeFormStepIndex) }
    }))
  }, [activeFormStepIndex])

  useEffect(() => {
    setBreadcrumbs(
      breadCrumbs.map((b, index) => {
        if (index === (breadCrumbs.length - 1)) {
          return {
            ...b,
            link: enableReview(),
            onClick: enableReview() ? () => setActiveFormStepIndex(index) : null,
          }
        }

        return {
          ...b,
          link: true,
          onClick: () => setActiveFormStepIndex(index),
        }
      }),
    )
  }, [enableReview])

  // ---- Render ----- //
  return (
    <section>
      <FormSection>
        <Centered>
          <Breadcrumb
            icon="right angle"
            size="large"
            sections={breadCrumbs}
          />
        </Centered>
      </FormSection>

      <FormSection>
        {getFormStepComponent()}
      </FormSection>

      <FormSection>
        <FormStepButtons
          isLastStep={activeFormStepIndex === (formSteps.length - 1)}
          onNext={() => setActiveFormStepIndex(Math.min(activeFormStepIndex + 1, formSteps.length - 1))}
          onBack={() => setActiveFormStepIndex(Math.max(0, activeFormStepIndex - 1))}
          enableNext={enableNext()}
          enableSubmit={enableReview()}
          onSubmit={() => alert('Yay')}
        />
      </FormSection>

      <FormSection>
        <Centered>
          <Breadcrumb
            icon="right angle"
            size="small"
            sections={breadCrumbs}
          />
        </Centered>
      </FormSection>
    </section>
  )
}

DataLoadingWizardForm.propTypes = {
  project: PropTypes.object,
}

export default DataLoadingWizardForm
