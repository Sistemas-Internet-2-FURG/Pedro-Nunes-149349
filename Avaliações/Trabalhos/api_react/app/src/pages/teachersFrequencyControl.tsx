import React, { useState, useEffect } from "react";
import axios from "../utils/axiosConfig.tsx";
import { Table, Alert, Card, Spin, Button, Form, Input, Modal } from "antd";
import { QRCodeCanvas } from "qrcode.react";
import "tailwindcss/tailwind.css";

const TeachersFrequencyControl = () => {
  interface Student {
    nome: string;
    matricula: string;
    presencas: number;
  }
  
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [qrCodeVisible, setQrCodeVisible] = useState(false);
  const [qrCodeValue, setQrCodeValue] = useState("");

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        const response = await axios.get("/api/chamada");
        let alunos = response.data.alunos;
        const dict_to_array = Object.keys(alunos).map((key) => {
          return {
            nome: key,
            matricula: alunos[key].matricula,
            presencas: alunos[key].presencas,
          };
        });
        setStudents(dict_to_array);
        setLoading(false);
      } catch (err) {
        setError("Failed to fetch students");
        setLoading(false);
      }
    };

    fetchStudents();
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

  const handleAddPresence = async (matricula, name) => {
    try {
      await axios.post(`/api/presenca/${name}/${matricula}`);
      setSuccess(`Presence of ${name} recorded successfully`);
      setError("");
      // Refresh the students list
      const response = await axios.get("/api/chamada");
      let alunos = response.data.alunos;
      const dict_to_array = Object.keys(alunos).map((key) => {
        return {
          nome: key,
          matricula: alunos[key].matricula,
          presencas: alunos[key].presencas,
        };
      });
      setStudents(dict_to_array);
    } catch (err) {
      setError(`Failed to record presence for ${name}`);
      setSuccess("");
    }
  };

  const handleRemoveStudent = async (name) => {
    try {
      const r = await axios.delete(`/api/chamada/${name}`);
      console.log(r.data);
      setSuccess(`Student ${name} removed successfully`);
      setError("");
      // Refresh the students list
      const response = await axios.get("/api/chamada");
      let alunos = response.data.alunos;
      const dict_to_array = Object.keys(alunos).map((key) => {
        return {
          nome: key,
          matricula: alunos[key].matricula,
          presencas: alunos[key].presencas,
        };
      });

      setStudents(dict_to_array);
    } catch (err) {
      setError(`Failed to remove student ${name}`);
      setSuccess("");
    }
  };

  const handleAddStudent = async (values) => {
    try {
      await axios.post("/api/chamada", {
        nome: values.nome,
        matricula: values.matricula,
        type: "Adicionar",
      });
      setSuccess("Student added successfully");
      setError("");
      // Refresh the students list
      const response = await axios.get("/api/chamada");
      const dict_to_array = Object.keys(response.data.alunos).map((key) => {
        return {
          nome: key,
          matricula: response.data.alunos[key].matricula,
          presencas: response.data.alunos[key].presencas,
        };
      });
      setStudents(dict_to_array);
    } catch (err) {
      setError("Failed to add student");
      setSuccess("");
    }
  };

  const handleShowQrCode = async () => {
    try {
      const response = await axios.get("/api/user/me"); // Supondo que esta rota retorna os dados do professor logado
      const token = response.data.token; // Supondo que o token está nos dados do professor
      const qrCodeUrl = `http://172.17.0.1/presenca_aluno/${token}`;
      setQrCodeValue(qrCodeUrl);
      setQrCodeVisible(true);
    } catch (err) {
      setError("Failed to generate QR Code");
    }
  };

  const columns = [
    {
      title: "Name",
      dataIndex: "nome",
      key: "nome",
      width: "50%",
    },
    {
      title: "Student Number",
      dataIndex: "matricula",
      key: "matricula",
      width: "20%",
    },
    {
      title: "Frequency",
      dataIndex: "presencas",
      key: "presencas",
      width: "5%",
    },
    {
      title: "Actions",
      key: "actions",
      width: "25%",
      render: (text, record) => (
        <div className="flex gap-2">
          <Button
            type="primary"
            onClick={() => handleAddPresence(record.matricula, record.nome)}
          >
            Add
          </Button>
          <Button
            type="primary" danger
            onClick={() => handleRemoveStudent(record.nome)}
          >
            Remove
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <Card className="w-full max-w-4xl p-4 shadow-sm">
        <h2 className="text-center mb-5 text-blue-600 font-bold">
          Teacher Frequency Control
        </h2>
        {loading ? (
          <div className="flex justify-center items-center">
            <Spin size="large" />
          </div>
        ) : (
          <>
            {error && <Alert message={error} type="error" className="mb-4" />}
            {students.length === 0 ? (
              <Alert message="No students found" type="warning" className="mb-4" />
            ) : (
              <Table
                dataSource={students}
                columns={columns}
                rowKey="nome"
                pagination={false}
                className="bg-lightgray"
              />
            )}
            {success && <Alert message={success} type="success" className="mt-4" />}
          </>
        )}
        <Form
          name="addStudent"
          onFinish={handleAddStudent}
          className="mt-4"
        >
          <Form.Item
            label="Name"
            name="nome"
            rules={[{ required: true, message: 'Please input the name!' }]}
          >
            <Input placeholder="Enter name" />
          </Form.Item>
          <Form.Item
            label="Student Number"
            name="matricula"
            rules={[{ required: true, message: 'Please input the student number!' }]}
          >
            <Input placeholder="Enter student number" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              Add Student
            </Button>
          </Form.Item>
        </Form>
        <Button type="primary" onClick={handleShowQrCode} className="mt-4">
          Show QR Code
        </Button>
        <Modal
          title="QR Code"
          visible={qrCodeVisible}
          onCancel={() => setQrCodeVisible(false)}
          footer={null}
        >
          <div className="flex justify-center">
            <QRCodeCanvas value={qrCodeValue} size={256} />
          </div>
        </Modal>
      </Card>
    </div>
  );
};

export default TeachersFrequencyControl;