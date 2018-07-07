/*
 * LoginPage
 *
 * This is the '/login' route
 */

import React from 'react';
import PropTypes from 'prop-types';
import { Helmet } from 'react-helmet';
import { FormattedMessage } from 'react-intl';
import { connect } from 'react-redux';
import { compose } from 'redux';
import { createStructuredSelector } from 'reselect';

import injectReducer from 'utils/injectReducer';
import H2 from 'components/H2';
import CenteredSection from './CenteredSection';
import Form from './Form'
import Input from './Input';
import Button from './Button';
import Link from './Link';
import messages from './messages';
import { changeUsername, changePassword } from './actions';
import { makeSelectUsername, makeSelectPassword } from './selectors';
import reducer from './reducer';

/* eslint-disable react/prefer-stateless-function */
export class LoginPage extends React.PureComponent {

  componentDidMount() {
    if (this.props.username && this.props.username.trim().length > 0 && this.props.password && this.props.password.trim().length > 0) {
      this.props.onSubmitForm();
    }
  }

  render() {
    return (
      <article>
        <Helmet>
          <title>Login Page</title>
          <meta
            name="description"
            content="An EACH application loginpage"
          />
        </Helmet>
        <div>
          <CenteredSection>
            <Form>
              <label htmlFor="username">
                <Input
                  id="username"
                  type="text"
                  placeholder="LOGIN"
                  value={this.props.username}
                  onChange={this.props.onChangeUsername}
                />
              </label>
              <br />
              <label htmlFor="password">
                <Input
                  id="password"
                  type="password"
                  placeholder="PASSWORD"
                  value={this.props.password}
                  onChange={this.props.onChangePassword}
                />
              </label>
              <br />
              <label htmlFor="signin">
                <Button
                  id="signin"
                  type="submit"
                  value="SIGN IN"
                  onClick={this.props.onSubmitForm}
                />
              </label>
            </Form>
            <Link to="/registration">
              <FormattedMessage {...messages.registration} />
            </Link>
          </CenteredSection>
        </div>
      </article>
    );
  }
}

LoginPage.propTypes = {
  onSubmitForm: PropTypes.func,
  username: PropTypes.string,
  onChangeUsername: PropTypes.func,
  password: PropTypes.string,
  onChangePassword: PropTypes.func,
};

export function mapDispatchToProps(dispatch) {
  return {
    onChangeUsername: evt => dispatch(changeUsername(evt.target.value)),
    onChangePassword: evt => dispatch(changePassword(evt.target.value)),
    onSubmitForm: evt => {
      if (evt !== undefined && evt.preventDefault) evt.preventDefault();
      console.log("Try Sign in");
    },
  };
}

const mapStateToProps = createStructuredSelector({
  username: makeSelectUsername(),
  password: makeSelectPassword(),
});

const withConnect = connect(
  mapStateToProps,
  mapDispatchToProps,
);

const withReducer = injectReducer({ key: 'login', reducer });

export default compose(
  withReducer,
  withConnect,
)(LoginPage);
