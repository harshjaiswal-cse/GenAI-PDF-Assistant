import { useRef, useState } from "react";
import api from "../services/api";

function Sidebar() {
  const fileInputRef = useRef();

  const [uploadedFiles, setUploadedFiles] = useState([]);

  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];

    if (!file) return;

    const formData = new FormData();

    formData.append("file", file);

    try {
      const response = await api.post(
        "/upload-pdf/",
        formData
      );

      alert("PDF Uploaded Successfully ✅");

      setUploadedFiles((prev) => [
        ...prev,
        response.data.filename,
      ]);

    } catch (error) {
      console.error(error);
      alert("Upload Failed ❌");
    }
  };

  return (
    <div className="sidebar">
      <h2>🚀 GenAI PDF Assistant</h2>

      <input
        type="file"
        accept=".pdf"
        ref={fileInputRef}
        style={{ display: "none" }}
        onChange={handleFileChange}
      />

      <button
        className="upload-btn"
        onClick={handleUploadClick}
      >
        📄 Upload PDF
      </button>

      <div className="files">
        <p>Uploaded Files</p>

        {uploadedFiles.map((file, index) => (
          <div
            key={index}
            className="file-item"
          >
            {file}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Sidebar;