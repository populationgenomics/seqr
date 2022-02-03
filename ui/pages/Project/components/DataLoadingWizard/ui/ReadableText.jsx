import styled from 'styled-components'
import PropTypes from 'prop-types'

const ReadableText = styled.p`
  font-size: ${props => props.fontSize};
  line-height: ${props => props.lineHeight};
`

ReadableText.propTypes = {
  fontSize: PropTypes.string,
  lineHeight: PropTypes.number,
}

ReadableText.defaultProps = {
  fontSize: '16px',
  lineHeight: 1.6,
}

export default ReadableText
