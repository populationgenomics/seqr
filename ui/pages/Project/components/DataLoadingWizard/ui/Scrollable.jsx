import styled from 'styled-components'
import PropTypes from 'prop-types'

const Scrollable = styled.div`
  overflow-x: ${props => props.x};
  overflow-y: ${props => props.y};
`

Scrollable.propTypes = {
  x: PropTypes.oneOf(['visible', 'hidden', 'scroll', 'auto', 'initial', 'inherit']),
  y: PropTypes.oneOf(['visible', 'hidden', 'scroll', 'auto', 'initial', 'inherit']),
}

Scrollable.defaultProps = {
  x: 'initial',
  y: 'initial',
}

export default Scrollable
