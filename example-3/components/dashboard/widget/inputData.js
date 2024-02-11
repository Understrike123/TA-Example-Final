import { useState } from "react";

const InputData = ({ onInputChange }) => {
  const [inputValue1, setInputValue1] = useState("");
  const [inputValue2, setInputValue2] = useState("");
  const [inputValue3, setInputValue3] = useState("");
  const [inputValue4, setInputValue4] = useState("");

  const handleInputChange1 = (e) => {
    const value = e.target.value;
    setInputValue1(value);
    onInputChange(value);
  };

  const handleInputChange2 = (e) => {
    const value = e.target.value;
    setInputValue2(value);
    onInputChange(value);
  };
  const handleInputChange3 = (e) => {
    const value = e.target.value;
    setInputValue3(value);
    onInputChange(value);
  };
  const handleInputChange4 = (e) => {
    const value = e.target.value;
    setInputValue4(value);
    onInputChange(value);
  };
  const label = ["Amplitude", "CMP Inc", "X-label Orientation", "Plot Height"];
  const name = ["Amplitude", "CMP Inc", "X-label Orientation", "Plot Height"];
  return (
    <div>
      <label>{label[0]}</label>
      <input
        name={name[0]}
        type="number"
        value={inputValue1}
        onChange={handleInputChange1}
        className="w-full px-4 py-2 rounded-md border border-white focus:outline-none focus:border-blue-300"
      />

      <br></br>
      <label>{label[1]}</label>
      <input
        name={name[1]}
        type="number"
        value={inputValue2}
        onChange={handleInputChange2}
        className="w-full px-4 py-2 rounded-md border border-white focus:outline-none focus:border-blue-300"
      />

      <br></br>
      <label>{label[2]}</label>
      <input
        name={name[2]}
        type="number"
        value={inputValue3}
        onChange={handleInputChange3}
        className="w-full px-4 py-2 rounded-md border border-white focus:outline-none focus:border-blue-300"
      />

      <br></br>
      <label>{label[3]}</label>
      <input
        name={name[3]}
        type="number"
        value={inputValue4}
        onChange={handleInputChange4}
        className="w-full px-4 py-2 rounded-md border border-white focus:outline-none focus:border-blue-300"
      />

      <br></br>
    </div>
  );
};

export default InputData;
