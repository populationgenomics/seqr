import React from 'react'
import PropTypes from 'prop-types'
import { Button } from 'semantic-ui-react'
import styled from 'styled-components'

const FormButtonGroup = styled.div`
  display: flex;
  justify-content: right;
`

const FormStepButtons = ({ isLastStep, onNext, onBack, onSubmit, enableNext, enableSubmit, loading, size }) => {
  const submitButton = (
    <Button
      size={size}
      onClick={onSubmit}
      negative
      disabled={!enableSubmit}
      loading={loading}
    >
      Submit
    </Button>
  )

  return (
    <FormButtonGroup>
      <Button
        size={size}
        onClick={onBack}
        loading={loading}
      >Back
      </Button>
      <Button
        size={size}
        onClick={onNext}
        disabled={!enableNext}
        loading={loading}
      >
        Next
      </Button>
      {
          isLastStep ? submitButton : null
      }
    </FormButtonGroup>
  )
}

FormStepButtons.propTypes = {
  isLastStep: PropTypes.bool,
  onNext: PropTypes.func,
  onBack: PropTypes.func,
  onSubmit: PropTypes.func,
  enableNext: PropTypes.bool,
  enableSubmit: PropTypes.bool,
  loading: PropTypes.bool,
  size: PropTypes.string,
}

FormStepButtons.defaultProps = {
  isLastStep: false,
  onNext: () => {},
  onBack: () => {},
  onSubmit: () => {},
  enableNext: false,
  enableSubmit: false,
  loading: false,
  size: 'small',
}

export default FormStepButtons
