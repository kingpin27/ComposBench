import './App.css';
import {useState, useEffect} from 'react'

function App() {
  const [imgUrl, setImgUrl] = useState("")
  
  useEffect(() => {
    async function fetchData() {
      try {
        const val = await fetch('http://localhost:8000/val.json')
                            .then(val => val.json())
        const random = ~~(Math.random() * val.length)
        const id = val[random]["reference_img_id"]
        const length = String(id).length
        const repeating_pattern = "0".repeat(12-length)
        setImgUrl("http://localhost:8000/image/" + repeating_pattern + String(id) + ".jpg")
      }
      catch (err) {
        console.error(err)
      }
    }
    fetchData()
  }, [])
  return (
    <div className="App">
      {imgUrl && <img src={imgUrl}/>}
    </div>
  );
}

export default App;
