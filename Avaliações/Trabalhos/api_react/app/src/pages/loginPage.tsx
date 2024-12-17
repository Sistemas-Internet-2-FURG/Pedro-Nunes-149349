import React, { useState } from "react";
import axios from "../utils/axiosConfig.tsx";
import { Form, Input, Button, Alert, Card, Spin } from "antd";
import { useNavigate } from "react-router-dom";
import "tailwindcss/tailwind.css";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const data = {
        matricula: values.registernumber,
        password: values.password,
      }
      const response = await axios.post("/api/login", data);
      setMessage(response.data.message);
      setError("");
      localStorage.setItem("token", response.data.token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`;
      if (response.data.user.isTeacher) {
        navigate("/teachersFrequency");
      } else{
        navigate("/studentsFrequency");
      }
    } catch (error) {
      setError(error.response?.data?.error || "Login failed");
      setMessage("");
    } finally {
      setLoading(false);
    }
  };

  const onFinishFailed = (errorInfo) => {
    console.log('Failed:', errorInfo);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <Card className="w-full max-w-md p-4 shadow-sm">
        <h3 className="text-center mb-4 text-blue-600 font-bold">
          ChamadinhaTop - Login
        </h3>
        <Form
          name="login"
          labelCol={{ span: 8 }}
          wrapperCol={{ span: 16 }}
          initialValues={{ remember: true }}
          onFinish={handleSubmit}
          onFinishFailed={onFinishFailed}
          autoComplete="off"
        >
            <Form.Item
            label="Registration"
            name="registernumber"
            rules={[{ required: true, message: 'Please input your registration number!' }]}
            >
            <Input
              placeholder="123456"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
            />
            </Form.Item>

          <Form.Item
            label="Password"
            name="password"
            rules={[{ required: true, message: 'Please input your password!' }]}
          >
            <Input.Password
              placeholder="********"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
            />
          </Form.Item>

          {error && (
            <Alert message={error} type="error" className="mt-3 text-brown" />
          )}
          {message && (
            <Alert message={message} type="success" className="mt-3" />
          )}

          <Form.Item wrapperCol={{ offset: 8, span: 16 }}>
            <Button
              type="primary"
              htmlType="submit"
              className="w-full py-2 mt-4 bg-blue-600 text-white font-bold rounded-md hover:bg-blue-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Spin size="small" />
                  Logging in...
                </>
              ) : (
                "Login"
              )}
            </Button>
          </Form.Item>

          <Form.Item wrapperCol={{ offset: 8, span: 16 }}>
            <Button
              type="link"
              href="/signin"
              className="w-full mt-2 text-center text-gray-500 hover:text-blue-600"
            >
              Go to Signin
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Login;