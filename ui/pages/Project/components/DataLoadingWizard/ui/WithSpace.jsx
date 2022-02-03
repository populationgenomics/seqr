import styled from 'styled-components'
import PropTypes from 'prop-types'

const WithSpace = styled.div`
  ${props => `${props.type}-top: ${props.top}`};
  ${props => `${props.type}-bottom: ${props.bottom}`};
  ${props => `${props.type}-left: ${props.left}`};
  ${props => `${props.type}-right: ${props.right}`};
`

WithSpace.propTypes = {
  type: PropTypes.oneOf(['padding', 'margin']),
  top: PropTypes.string,
  bottom: PropTypes.string,
  left: PropTypes.string,
  right: PropTypes.string,
}

WithSpace.defaultProps = {
  type: 'margin',
  top: 'initial',
  bottom: 'initial',
  left: 'initial',
  right: 'initial',
}

export default WithSpace
