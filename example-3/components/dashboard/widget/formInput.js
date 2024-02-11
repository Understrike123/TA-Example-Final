import React, { useState, useEffect } from "react";

const FormComponent = () => {
  // State untuk menyimpan nilai dropdown dan input number
  const [selectedOption, setSelectedOption] = useState("gray");
  const [numberValues, setNumberValues] = useState(["435", "100", "10", "800"]);

  // Fungsi untuk menangani perubahan nilai dropdown
  const handleDropdownChange = (event) => {
    setSelectedOption(event.target.value);
  };

  // Fungsi untuk menangani perubahan nilai input number
  const handleNumberInputChange = (event, index) => {
    const newNumberValues = [...numberValues];
    newNumberValues[index] = event.target.value;
    setNumberValues(newNumberValues);
  };

  // Fungsi untuk mengirim data ke server Flask
  const [imageData, setImageData] = useState(null);
  const sendDataToFlask = async () => {
    // Menyiapkan data untuk dikirim
    const formData = {
      colr: selectedOption,
      amp: numberValues[0],
      cmpinc: numberValues[1],
      textcanvas: numberValues[2],
      xlaborient: numberValues[3],
    };

    // Kirim data ke server Flask
    try {
      const response = await fetch("http://127.0.0.1:5000/seisview2d", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });
      const data = await response.json();
      setImageData(data);
      console.log(data); // Lakukan sesuatu dengan respons dari server jika diperlukan
    } catch (error) {
      console.error("Error:", error);
    }
  };

  // Mengirim data ke server Flask saat komponen dimuat
  useEffect(() => {
    sendDataToFlask();
  }, []); // Penambahan [] membuat useEffect hanya dijalankan sekali saat komponen dimuat

  return (
    <form onSubmit={(event) => event.preventDefault()}>
      <div>
        <div>
          {imageData && (
            <img
              src={`data:image/${imageData.image_format};base64,${imageData.image}`}
              alt="Image"
            />
          )}
        </div>
        <label htmlFor="dropdown">Pilihan:</label>
        <select
          id="dropdown"
          value={selectedOption}
          onChange={handleDropdownChange}
        >
          <option value="gray">Gray</option>
          <option value="RdGy">RdGy</option>
          <option value="BrBg">BrBg</option>
          <option value="coolwarm">Coolwarm</option>
          <option value="RdBu">RdBu</option>
          <option value="spectral">Spectral</option>
          <option value="fire">Fire</option>
          <option value="magma">Magma</option>
          <option value="seismic">Seismic</option>
          <option value="bwr">Bwr</option>
          <option value="jet">Jet</option>
        </select>
      </div>
      <div>
        <label htmlFor="number1">Number 1:</label>
        <input
          type="number"
          id="number1"
          value={numberValues[0]}
          onChange={(event) => handleNumberInputChange(event, 0)}
        />
      </div>
      <div>
        <label htmlFor="number2">Number 2:</label>
        <input
          type="number"
          id="number2"
          value={numberValues[1]}
          onChange={(event) => handleNumberInputChange(event, 1)}
        />
      </div>
      <div>
        <label htmlFor="number3">Number 3:</label>
        <input
          type="number"
          id="number3"
          value={numberValues[2]}
          onChange={(event) => handleNumberInputChange(event, 2)}
        />
      </div>
      <div>
        <label htmlFor="number4">Number 4:</label>
        <input
          type="number"
          id="number4"
          value={numberValues[3]}
          onChange={(event) => handleNumberInputChange(event, 3)}
        />
      </div>
      <button onClick={sendDataToFlask}>Submit</button>
    </form>
  );
};

export default FormComponent;
