import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import './App.css';
import Login from "./pages/loginPage.tsx";
import Register from "./pages/registerPage.tsx";
import StudentsFrequencyControl from "./pages/studentsFrequencyPage.tsx";
import TeachersFrequencyControl from "./pages/teachersFrequencyControl.tsx";
// import GifScreen from "./pages/gif.tsx";
function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signin" element={<Register />} />
          <Route path="/studentsFrequency" element={<StudentsFrequencyControl />} />
          <Route path="/teachersFrequency" element={<TeachersFrequencyControl />} />
          {/* <Route path="/gif" element={<GifScreen />} /> */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
