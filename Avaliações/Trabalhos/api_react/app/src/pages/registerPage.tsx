import React, { useState } from "react";
import { Form, Input, Button, Checkbox, Alert, Card } from "antd";
import axios from "../utils/axiosConfig.tsx";
import { useNavigate } from "react-router-dom";

const Signin = () => {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const data = {
        name: values.name,
        email: values.email,
        studentNumber: values.studentNumber,
        password: values.password,
        isTeacher: values.isTeacher || false,
      }

      const response = await axios.post("/api/signin", data);
      setError("");
      localStorage.setItem("token", response.data.token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`;
      if (response.data.user.isTeacher) {
        navigate("/teachersFrequency");
      }
      else {
        navigate("/studentsFrequency");
      }
      // Handle successful signin
    } catch (error) {
      setError(error.response?.data?.error || "Signin failed");
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
        <h2 className="text-center mb-5 text-cornflowerblue font-bold">
          Flask - Login
        </h2>
        <Form
          name="signin"
          labelCol={{ span: 8 }}
          wrapperCol={{ span: 16 }}
          initialValues={{ remember: true }}
          onFinish={handleSubmit}
          onFinishFailed={onFinishFailed}
          autoComplete="off"
        >
          <Form.Item
            label="Name"
            name="name"
            rules={[{ required: true, message: 'Please input your name!' }]}
          >
            <Input
              type="text"
              placeholder="Your name"
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
            />
          </Form.Item>

          <Form.Item
            label="Email address"
            name="email"
            rules={[{ required: true, message: 'Please input your email!' }]}
          >
            <Input
              type="email"
              placeholder="example@email.com"
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
            />
            
          </Form.Item>

          <small className="form-text text-muted">
              We will never share your email with anyone.
            </small>

          <Form.Item
            label="Register Number"
            name="studentNumber"
            rules={[{ required: true, message: 'Please input your register number!' }]}
          >
            <Input
              type="number"
              placeholder="Your Register Number"
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
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
            />
          </Form.Item>

          <Form.Item
            name="isTeacher"
            valuePropName="checked"
            wrapperCol={{ offset: 8, span: 16 }}
          >
            <Checkbox>
              I'm a teacher
            </Checkbox>
          </Form.Item>

          {error && (
            <Alert message={error} type="error" className="mt-3 text-brown" />
          )}

          <Form.Item wrapperCol={{ offset: 8, span: 16 }}>
            <Button
              type="primary"
              htmlType="submit"
              className="w-full py-2 mt-4 bg-blue-600 text-white font-bold rounded-md hover:bg-blue-700 disabled:opacity-50"
              disabled={loading}
            >
              Submit
            </Button>
          </Form.Item>

          <Form.Item wrapperCol={{ offset: 8, span: 16 }}>
            <Button
              type="link"
              href="/login"
              className="w-full mt-2 text-center text-gray-500 hover:text-blue-600"
            >
              Go to Login
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Signin;