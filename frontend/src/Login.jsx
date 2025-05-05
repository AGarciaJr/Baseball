import React, { useState } from 'react';
import './styles.css';
import axios from 'axios';

const API_URL = "http://localhost:5000";

export default function Login({ onSwitch }) {
  const [form, setForm] = useState({ username: '', password: '' });
  const [errors, setErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (!form.username.trim()) errs.username = 'Username is required';
    if (!form.password) errs.password = 'Password is required';
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
      const response = await axios.post(
        `${API_URL}/api/user/login?username=${form.username}&password=${form.password}`,
        {}, 
        {
          withCredentials: true,
          headers: {
            'Content-Type': 'text/html', // Not typical for login, might want to change
          },
        }
      );
      console.log(response.body); 
      location.reload();
    }
  };

  return (
    <div className="app">
      <form className="form-container" onSubmit={handleSubmit}>
        <h1>Log In</h1>

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

        <button className="form-button" type="submit">
          Log In
        </button>

        <div className="form-toggle">
          Don’t have an account?{' '}
          <span onClick={onSwitch}>Sign up</span>
        </div>
      </form>
    </div>
  );
}
