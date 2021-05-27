import React from 'react'
import { shallow, configure } from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'
import { BaseLayoutComponent } from './BaseLayout'

configure({ adapter: new Adapter() })

test('shallow-render without crashing', () => {
  /*
    user: PropTypes.object.isRequired,
    children: PropTypes.node,
   */

  const props = {
    user: {
      date_joined: '2015-02-19T20:22:50.633Z',
      email: 'test@populationgenomics.org.au',
      first_name: '',
      id: 1,
      is_active: true,
      last_login: '2017-03-14T17:44:53.403Z',
      last_name: '',
      username: 'test',
    },
    children: [],
  }

  shallow(<BaseLayoutComponent {...props} />)
})
