/* eslint-disable react-perf/jsx-no-new-function-as-prop */
/* eslint-disable no-console */
/* eslint-disable no-alert */

import React, { useState, useEffect, useCallback } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Breadcrumb } from 'semantic-ui-react'

import { Error404 } from '../../../../shared/components/page/Errors'
import { getCurrentProject } from '../../selectors'

import { Centered, FormSection, FormStepButtons } from './ui'
import { Welcome, TemplateUpload } from './steps'
import PedigreeTemplateColumns from './templates/Pedigree'
import IndividualTemplateColumns from './templates/Individual'
import FamilyTemplateColumns from './templates/Family'
import TemplateFile from './templates/File/TemplateFile'
import TemplateHelp from './TemplateHelp'

const BREADCRUMBS = [
  { key: 0, content: 'Welcome', link: true, active: true },
  { key: 1, content: 'Pedigree', link: true, active: false },
  { key: 2, content: 'Individual metadata', link: true, active: false },
  { key: 3, content: 'Family metadata', link: true, active: false },
  { key: 4, content: 'Sample mapping', link: true, active: false },
  { key: 5, content: 'Review', link: true, active: false },
]

const BaseMultistepForm = ({ project }) => {
  // ---- Debug ---- //
  console.group('Project Object')
  console.log(project)
  console.groupEnd()

  // ---- State ----- //
  const [breadCrumbs, setBreadcrumbs] = useState(BREADCRUMBS.map(b => ({ ...b })))
  const [activeFormStepIndex, setActiveFormStepIndex] = useState(0)
  const [formSteps, setFormSteps] = useState(BREADCRUMBS.map(
    (_, index) => ({ formData: {}, isComplete: (index === 0) }),
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
  }, [formSteps])

  const enableReview = useCallback(() => formSteps
    .slice(0, formSteps.length - 1)
    .reduce((acc, step) => acc && step.isComplete, true), [formSteps])

  const enableNext = useCallback(() => {
    if (activeFormStepIndex === (formSteps.length - 2)) {
      return enableReview()
    }

    return activeFormStepIndex < formSteps.length
  }, [formSteps, activeFormStepIndex, enableReview])

  const getFormStepComponent = useCallback(() => {
    const onFormChange = ({ formData, isComplete }) => updateFormStep(activeFormStepIndex, { formData, isComplete })

    switch (activeFormStepIndex) {
      case 0:
        return <Welcome />
      case 1:
        return (
          <TemplateUpload
            id="pedigree-upload"
            key="pedigree-upload"
            label="Pedigree"
            template={new TemplateFile(PedigreeTemplateColumns())}
            onFormChange={onFormChange}
            information={<TemplateHelp />}
            project={project}
          />
        )
      case 2:
        return (
          <TemplateUpload
            id="individual-metadata-upload"
            key="individual-metadata-upload"
            label="Individual Metadata"
            template={new TemplateFile(IndividualTemplateColumns())}
            onFormChange={onFormChange}
            information={<TemplateHelp />}
            project={project}
          />
        )
      case 3:
        return (
          <TemplateUpload
            id="family-metadata-upload"
            key="family-metadata-upload"
            label="Family Metadata"
            template={new TemplateFile(FamilyTemplateColumns())}
            onFormChange={onFormChange}
            information={<TemplateHelp />}
            project={project}
          />
        )
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
    setBreadcrumbs(breadCrumbs.map((b, index) => ({ ...b, active: (index === activeFormStepIndex) })))
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

BaseMultistepForm.propTypes = {
  project: PropTypes.object.isRequired,
}

const mapStateToProps = state => ({
  project: getCurrentProject(state),
})

export const MultistepForm = connect(mapStateToProps)(BaseMultistepForm)

const DataLoadingWizard = () => <MultistepForm />

export default DataLoadingWizard
