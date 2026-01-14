class Timer:
  def __init__(self):
    self.time = 0
    self.tally = 0
    self.reverse = False
    self.ticked = False

  def timer(self, duration=int):
    self.time += 1
    if self.time >= duration:
      self.time = 0
      return True
    else: return False

  def wait(self, duration=int, lag=2):
    self.time += 1
    if self.time >= duration:
      if self.time >= duration * lag:
        self.time = 0
      return True
    else: return False
  
  def count(self, duration=int, stop=int, start=0):
    if self.time == 0 and self.tally == 0:
      self.tally = start
    if self.tally < stop:
      self.time += 1
      if self.time >= duration:
        self.time = 0
        self.tally += 1
    return self.tally
  
  def subcount(self, duration=int, stop=int, start=int):
    if self.time == 0 and self.tally == 0:
      self.tally = start
    if self.tally > stop:
      self.time += 1
      if self.time >= duration:
        self.time = 0
        self.tally -= 1
    return self.tally

  def keep_count(self, duration=int, stop=int, start=0):
    if self.time == 0 and self.tally == 0:
      self.tally = start
    if self.tally < stop:
      self.time += 1
      if self.time >= duration:
        self.time = 0
        self.tally += 1
        if self.tally >= stop:
          self.tally = start
    return self.tally
  
  def oscillate(self, duration=int, stop=int, start=0):
    if self.time == 0 and self.tally == 0: self.tally = start
    self.time += 1
    if self.time >= duration:
      self.time = 0
      if self.reverse: self.tally -= 1
      else: self.tally += 1
      if self.tally >= stop: self.reverse = True
      if self.tally < start: self.reverse = False
    return self.tally
  
  def nonstopcount(self, duration=int, start=0):
    if self.time == 0 and self.tally == 0:
      self.tally = start
    self.time += 1
    self.ticked = False
    if self.time >= duration:
      self.time = 0
      self.tally += 1
      self.ticked = True
    return self.tally
  
  def reset(self):
    self.time = 0
    self.tally = 0
    self.ticked = False

#print(len({"123": "6", "435": "456", "3": "7"}))
#print(["man",  "woman",  "kid",  "baby"][2:])
#dict = {}
#pleh = "bruh"
#dict[pleh] = "blaw"
#print(dict)
#for i in {"father": "man", "mother": "woman"}: print(i)
#dict1 = {"father": "man", "mother": "woman"}
#print(dict1.keys())
#print(list(dict1))
#print("man" in dict1)
#dict2 = dict1
#print(dict2)
#dict1["father"] = "transgender nigger"
#print(dict2)
#for i in range(39): fibbonacci = lambda x: x if x in (0, 1) else fibbonacci(x-1)+fibbonacci(x-2); print(str(i), str(fibbonacci(i)))