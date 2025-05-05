import React, { useState } from 'react';

const API_URL = "http://localhost:8080";

export default function CreateAccount({ onSwitch }) {
  const [form, setForm] = useState({
    username: '',
    password: '',
    confirm: ''
  });
  const [errors, setErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (!form.username.trim()) errs.username = 'Username is required';
    if (form.password.length < 6)
      errs.password = 'Password must be at least 6 characters';
    if (form.confirm !== form.password)
      errs.confirm = 'Passwords do not match';
    return errs;
  };

  const handleChange = e => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };

  const handleSubmit = async(e) => {
    e.preventDefault();
    const errs = validate();
    setErrors(errs);
    if (Object.keys(errs).length === 0) {
      const response = await fetch(`${API_URL}/api/user/create` + "?username=" + form.username + "&password=" + form.password, {
        method: 'POST',
        credentials: 'include'
      });
      console.log('Creating account with', form);
      location.reload();
    }
  };

  return (
    <div className="app">
      <form className="form-container" onSubmit={handleSubmit}>
        <h1>Create Account</h1>

        <div className="form-field">
          <label htmlFor="username">Username</label>
          <input
            className="form-input"
            id="username"
            name="username"
            type="text"
            value={form.username}
            onChange={handleChange}
            placeholder="your username"
          />
          {errors.username && <div className="form-error">{errors.username}</div>}
        </div>

        <div className="form-field">
          <label htmlFor="password">Password</label>
          <input
            className="form-input"
            id="password"
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            placeholder="••••••••"
          />
          {errors.password && <div className="form-error">{errors.password}</div>}
        </div>

        <div className="form-field">
          <label htmlFor="confirm">Confirm Password</label>
          <input
            className="form-input"
            id="confirm"
            name="confirm"
            type="password"
            value={form.confirm}
            onChange={handleChange}
            placeholder="••••••••"
          />
          {errors.confirm && <div className="form-error">{errors.confirm}</div>}
        </div>

        <button className="form-button" type="submit">
          Sign Up
        </button>
        <div className="form-toggle">
            Already have an account?{' '}
            <span onClick={onSwitch}>Log in</span>
       </div>
      </form>
    </div>
  );
}