import React, { useState, useEffect } from "react";
import axios from "../utils/axiosConfig.tsx";
import { Table, Alert, Card, Spin } from "antd";
import "tailwindcss/tailwind.css";

const StudentsFrequencyControl = () => {
  const [teachers, setTeachers] = useState<{ name: string; frequency: any }[]>([]);
  interface Teacher {
    name: string;
    frequency: any;
  }
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    const fetchTeachers = async () => {
      try {
        const response = await axios.get("/api/chamada");
        console.log(response.data);
        const dict_to_array = Object.keys(response.data.teachers).map(
          (key) => {
            return {
              name: key,
              frequency: response.data.teachers[key],
            };
          }
        );

        setTeachers(dict_to_array);
        setLoading(false);
      } catch (err) {
        setError("Failed to fetch teachers");
        setLoading(false);
      }
    };

    fetchTeachers();
  }, []);

  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        setError("");
        setSuccess("");
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, success]);

  const columns = [
    {
      title: "Teacher's name",
      dataIndex: "name",
      key: "name",
      width: "50%",
    },
    {
      title: "Frequency",
      dataIndex: "frequency",
      key: "frequency",
      width: "5%",
    },
  ];

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <Card className="w-full max-w-4xl p-4 shadow-sm">
        <h2 className="text-center mb-5 text-blue-600 font-bold">
          Students Frequency Control
        </h2>
        {loading ? (
          <div className="flex justify-center items-center">
            <Spin size="large" />
          </div>
        ) : (
          <>
            {error && (
              <Alert message={error} type="error" className="mb-4" />
            )}
            {teachers.length === 0 ? (
              <Alert message="No teachers found" type="warning" className="mb-4" />
            ) : (
              <Table
                dataSource={teachers}
                columns={columns}
                rowKey="name"
                pagination={false}
                className="bg-lightgray"
              />
            )}
            {success && (
              <Alert message={success} type="success" className="mt-4" />
            )}
          </>
        )}
      </Card>
    </div>
  );
};

export default StudentsFrequencyControl;
