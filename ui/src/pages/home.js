import { useState, useEffect } from 'react'
import "./home.css"
import Container from '@mui/material/Container'
import TextField from '@mui/material/TextField'
import InputAdornment from '@mui/material/InputAdornment'
import SearchIcon from '@mui/icons-material/Search';
import { Box, CircularProgress, IconButton, MenuItem, Select } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';

const Home = (props) => {
    const [imgUrl, setImgUrl] = useState("")
    const [modificationText, setModificationText] = useState("")
    const [valId, setValId] = useState(0)
    const [targetIds, setTargetIds] = useState([])
    const [algorithm, setAlgorithm] = useState("SEARLE")
    const [loading, setLoading] = useState(false)
    const [searchResults, setSearchResults] = useState([])

    const handleSearch = async () => {
        setLoading(true)
        setSearchResults([])
        try {
            const url = new URL('http://localhost:8000/search-val')
            url.searchParams.set('val_id', valId)
            url.searchParams.set('algo', algorithm)
            const results = await fetch(url.toString()).then(val => val.json())
            setSearchResults(results)
        }
        catch(e) {
            console.error(e)
        }
        finally {
            setLoading(false)
        }

    };

    const handleKeyDown = (event) => {
        if (event.key === 'Enter') {
            handleSearch();
        }
    };

    useEffect(() => {
        async function fetchData() {
            try {
                const val = await fetch('http://localhost:8000/val.json')
                    .then(val => val.json())
                const random = ~~(Math.random() * (val.length - 1))
                const id = val[random]["reference_img_id"]
                const length = String(id).length
                const repeating_pattern = "0".repeat(12 - length)
                setImgUrl("http://localhost:8000/image/" + repeating_pattern + String(id) + ".jpg")
                setValId(random)
                setModificationText(val[random]["relative_caption"])
                setTargetIds([val[random]["target_img_id"], ...val[random]["gt_img_ids"]])
            }
            catch (err) {
                console.error(err)
            }
        }
        fetchData()
    }, [])
    return (
        <div className='app-wrapper'>

            <Container maxWidth="sm" style={{display: 'flex', flexDirection: 'column', maxWidth: 600, alignItems: 'center', justifyContent: "start"}}>
                <Select 
                    style={{marginBottom: '50px', width: '250px'}}
                    value={algorithm}
                    onChange={(e) => setAlgorithm(e.target.value)}
                >
                    <MenuItem value={"SEARLE"}>SEARLE</MenuItem>
                </Select>
                {imgUrl && 
                    <Box sx={{ position: 'relative', display: 'inline-block' }}>
                        {/* The image itself */}
                        <img
                            src={imgUrl}
                            style={{ width: '100%', height: 'auto', display: 'block', marginBottom: '10px', borderRadius: '5px' }} // display: block helps with alignment issues
                        />

                        {/* 2. Position the IconButton absolutely within the container */}
                        <IconButton
                            sx={{
                            position: 'absolute',
                            top: 8, // Adjust as needed for desired margin
                            right: 8, // Adjust as needed for desired margin
                            color: 'white', // Optional: change icon color for better visibility
                            backgroundColor: 'rgba(0, 0, 0, 0.5)', // Optional: semi-transparent background
                            '&:hover': {
                                backgroundColor: 'rgba(0, 0, 0, 0.7)',
                            },
                            }}
                            aria-label="edit image"
                            onClick={() => alert('Edit button clicked!')}
                        >
                            <EditIcon />
                        </IconButton>
                    </Box>
                }
                <TextField
                    label="Modification Text"
                    variant="outlined"
                    fullWidth
                    value={modificationText}
                    onChange={(e) => setModificationText(e.target.value)}
                    onKeyDown={handleKeyDown}
                    rows={2}
                    multiline
                    InputProps={{
                        endAdornment: (
                        <InputAdornment position="end">
                            {
                                !loading && 
                                <IconButton onClick={handleSearch} aria-label="search">
                                    <SearchIcon />
                                </IconButton>
                            }
                            {
                                loading && 
                                <CircularProgress/>
                            }
                        </InputAdornment>
                        ),
                    }}
                    />
            </Container>
            <Container className='results-side'>
                {
                    searchResults.map((val, idx) => {
                        const img_id = Number(val["filename"].split('.')[0])
                        const isTarget = targetIds.includes(img_id)
                        return (
                            <div key={val["filename"]} style={{marginBottom: 50}}>
                                <img style={{borderRadius: '5px', ...(isTarget && {borderWidth: '10px', borderStyle: 'solid', borderColor: isTarget ? '#39FF14': 'black'})}} src={'http://localhost:8000/image/' + val['filename']}/>
                                <p style={{margin: 0}}>Score: {val['score']}</p>
                                <p style={{margin: 0}}>Rank: {idx+1}</p>
                            </div>
                        )
                    })
                }
            </Container>
        </div>
    );
}

export default Home;