# Hannah, an AI Life Coach (Powered by ChatGPT)

A slack bot that captures your thoughts, gives you suggestions, writes journals and makes to-do items on Trello

## Local Development

### Dependencies

    Python 3.10+
    Poetry

### First time install

Rename `config.example.yaml` to `config.yaml`, fill the variables

Then:

    poetry install


### Run the app

With hot reload in PyCharm:

    press the orange Play button (by Reloadium)

from CLI:

    python main.py


## Deployment

    docker-compose build
    docker-compose up -d


## Credits:

Prompt idea from [this YouTube Video (Chinese)](https://youtu.be/ZRv0Z-M7NqM).


## License

See the [LICENSE](LICENSE.md) file for license rights and limitations (MIT).
