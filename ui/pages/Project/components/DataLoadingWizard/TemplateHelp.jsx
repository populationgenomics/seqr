import React from 'react'

import { ReadableText } from './ui'
import TemplateDirectoryLink from './TemplateDirectoryLink'

const TemplateHelp = () => (
  <ReadableText>
    In this section, you will provide all information relating to the family pedigree and associated metadata in your
    project. Please download the families template from
    {' '}
    <TemplateDirectoryLink />
    { '. ' }
    Once you have filled in this template, upload it via this step and correct any validation errors before proceeding.
  </ReadableText>
)

export default TemplateHelp
