class RPCUrl:
    filler = "..."

    def __init__(self, url: str):
        self.url = url
        self._max_str_len = 31

    @property
    def short_url(self):
        sub_len = (self._max_str_len - len(self.filler)) // 2
        striped_url = self.url.split("://")[-1]

        return striped_url[:sub_len] + self.filler + striped_url[-sub_len:]
