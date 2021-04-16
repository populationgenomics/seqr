import React from 'react'
import PropTypes from 'prop-types'
import queryString from 'query-string'
import { connect } from 'react-redux'
import { Redirect } from 'react-router-dom'
import { Message, Button, Icon } from 'semantic-ui-react'

import { getGoogleLoginEnabled } from 'redux/selectors'
import { ANVIL_URL } from 'shared/utils/constants'
import { login } from '../reducers'

const Login = ({ location }) => {
  const queryParams = queryString.parse(location.search)
  const googleauthLoginUri = `/login/google-oauth2${location.search}`

  if (Object.keys(queryParams).length === 0 && !location.pathname.includes('google-oauth2')) {
    // no query parameters, so not a redirect, let's auto redirect to GCP login
    return (
      <div>
        <Redirect to={googleauthLoginUri} push />
        <p>Redirecting to Google login, click <a href={googleauthLoginUri}>here</a> if this isn&apost working as expected</p>
      </div>)
  }

  return (
    <div style={{ backgroundColor: 'white', maxWidth: '600px', width: '37%', minWidth: '300px', margin: '0 auto', padding: '40px', border: '1px solid rgba(34,36,38,.15)', borderRadius: '.28571429rem', boxShadow: '0 1px 2px 0 rgb(34 36 38 / 15%)' }}>
      <p style={{ textAlign: 'center' }}>
        <Button as="a" href={googleauthLoginUri} primary>
          <Icon name="google" />
          Sign in with Google
        </Button>
      </p>
      {queryParams.anvilLoginFailed &&
        <Message visible error>
          Unable to authorize the selected Google user. Please register your account in AnVIL by signing in and
          registering at <a href={ANVIL_URL} target="_blank">anvil.terra.bio</a>
        </Message>}
      {queryParams.googleLoginFailed &&
      <Message visible error>
        No seqr account found for the selected Google user
      </Message>}
    </div>
  )
}

Login.propTypes = {
  location: PropTypes.object,
}

const mapDispatchToProps = {
  onSubmit: login,
}

const mapStateToProps = state => ({
  googleLoginEnabled: getGoogleLoginEnabled(state),
})

export default connect(mapStateToProps, mapDispatchToProps)(Login)
