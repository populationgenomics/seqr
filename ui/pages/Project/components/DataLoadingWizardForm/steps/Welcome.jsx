import React from 'react'
import styled from 'styled-components'

const WelcomeSection = styled.section`
  margin: 1em 0;
`

const ReadableText = styled.p`
  font-size: 16px;
  line-height: 1.6;
`

const Welcome = () => {
  return (
    <div>
      <WelcomeSection>
        <ReadableText>
          Welcome to the seqr data loading wizard! This wizard will guide you through the process of uploading
          the relevant individual template, family template and associated metadata files. Each step will validate
          these files to ensure that the information relating individuals, families and samples is correctly formatted.
        </ReadableText>
      </WelcomeSection>

      <WelcomeSection>
        <h2>Introduction</h2>
        <ReadableText>Overview of what the collaborator needs to do goes here</ReadableText>
      </WelcomeSection>

      <WelcomeSection>
        <h2>Resources</h2>
        <ReadableText>Overview of required template and mapping formats</ReadableText>
      </WelcomeSection>

      <WelcomeSection>
        <h2>FAQ</h2>
        <ReadableText>Frequently asked questions and answers</ReadableText>
      </WelcomeSection>
    </div>
  )
}

export default Welcome

