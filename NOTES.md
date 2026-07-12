# Notes

The idea is to map the the following data points to the elements of sound. In order to do this, we need to play with what the `tone.js` library provides.

So for example, spotify API gives audio features like these

```json
{
  "acousticness": 0.00242,
  "analysis_url": "https://api.spotify.com/v1/audio-analysis/2takcwOaAZWiXQijPHIx7B",
  "danceability": 0.585,
  "duration_ms": 237040,
  "energy": 0.842,
  "id": "2takcwOaAZWiXQijPHIx7B",
  "instrumentalness": 0.00686,
  "key": 9,
  "liveness": 0.0866,
  "loudness": -5.883,
  "mode": 0,
  "speechiness": 0.0556,
  "tempo": 118.211,
  "time_signature": 4,
  "track_href": "https://api.spotify.com/v1/tracks/2takcwOaAZWiXQijPHIx7B",
  "type": "audio_features",
  "uri": "spotify:track:2takcwOaAZWiXQijPHIx7B",
  "valence": 0.428
}
```

We know for sure the data points 

- `lat / lng` - can be mapped to the panner 3D to identify the geolocation to give a sense of spatial quakes
- `depth` - can be mapped to bass effect of the sound
- `mag` - can be mapped to a note (lower notes for lesser values and higher notes for higher values)


Apart from the above, we can take every instrument 