import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { Breadcrumb, Header } from 'semantic-ui-react'

import { Centered, FormSection, FormStepButtons } from './ui'
import { Welcome } from './steps'

const FORM_STEPS = [
  { key: 0, content: 'Welcome', link: false, active: true, component: Welcome },
  { key: 1, content: 'Family metadata', link: false, active: false, component: () => {} },
  { key: 2, content: 'Individual metadata', link: false, active: false, component: () => {} },
  { key: 3, content: 'Sample mapping', link: false, active: false, component: () => {} },
  { key: 4, content: 'Submit', link: false, active: false, component: () => {} },
]

const DataLoadingWizardForm = ({ project }) => {
  // const [formState, setFormState] = useState({})
  const [formStepIndex, setFormStepIndex] = useState(0)
  const [formSteps, setFormSteps] = useState([...FORM_STEPS])

  useEffect(() => {
    setFormSteps(
      formSteps.map(
        (step) => { return { ...step, active: step.key === formStepIndex } },
      ),
    )
  }, [formStepIndex])

  return (
    <section>
      <FormSection>
        <Centered>
          <Breadcrumb
            icon="right angle"
            size="large"
            sections={formSteps}
          />
        </Centered>
      </FormSection>

      <FormSection>
        {/* React Hook components are just functions under the hood. */}
        {/* Get the component property from the current step and call it to add it to the DOM. */}
        {formSteps[formStepIndex].component({ project })}
        <Header>DEBUG</Header>
        <pre>{JSON.stringify(project, null, 2)}</pre>
      </FormSection>

      <FormSection>
        <FormStepButtons
          isLastStep={formStepIndex === (formSteps.length - 1)}
          onNext={() => setFormStepIndex(Math.min(formStepIndex + 1, formSteps.length - 1))}
          onBack={() => setFormStepIndex(Math.max(0, formStepIndex - 1))}
          onSubmit={() => alert('Yay')}
        />
      </FormSection>

      <FormSection>
        <Centered>
          <Breadcrumb
            icon="right angle"
            size="small"
            sections={formSteps}
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
