import React from 'react'
import PropTypes from 'prop-types'
import { Button } from 'semantic-ui-react'
import styled from 'styled-components'

const FormButtonGroup = styled.div`
  display: flex;
  justify-content: right;
`

const FormStepButtons = ({ isLastStep, onNext, onBack, onSubmit, disabled, loading, size }) => {
  if (isLastStep) {
    return (
      <FormButtonGroup>
        <Button
          size={size}
          onClick={onBack}
          disabled={disabled}
          loading={loading}
        >Back
        </Button>
        <Button
          size={size}
          onClick={onNext}
          disabled={disabled}
          loading={loading}
        >
          Next
        </Button>
        <Button
          size={size}
          onClick={onSubmit}
          negative
          disabled={disabled}
          loading={loading}
        >
          Submit
        </Button>
      </FormButtonGroup>
    )
  }

  return (
    <FormButtonGroup>
      <Button
        size={size}
        onClick={onBack}
        disabled={disabled}
        loading={loading}
      >Back
      </Button>
      <Button
        size={size}
        onClick={onNext}
        disabled={disabled}
        loading={loading}
      >
        Next
      </Button>
    </FormButtonGroup>
  )
}

FormStepButtons.propTypes = {
  isLastStep: PropTypes.bool,
  onNext: PropTypes.func,
  onBack: PropTypes.func,
  onSubmit: PropTypes.func,
  disabled: PropTypes.bool,
  loading: PropTypes.bool,
  size: PropTypes.string,
}

FormStepButtons.defaultProps = {
  isLastStep: false,
  onNext: () => {},
  onBack: () => {},
  onSubmit: () => {},
  disabled: false,
  loading: false,
  size: 'small',
}

export default FormStepButtons
