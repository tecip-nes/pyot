importPackage(java.io);

TIMEOUT(70000000)
NUM_NODES = 5;
TOPOLOGY = 0;
PYCO_NODE = 0;
LAST_PYCO_NODE = 5;
SENSOR_NODE = [2, 3];
ACTUATOR_NODE = 5;
NUM_SAMPLES_NODE = 2;
NUM_SAMPLES_TOT = NUM_SAMPLES_NODE * SENSOR_NODE.length;
NUM_POWERLOG_ENTRY = NUM_NODES * NUM_SAMPLES_TOT;
LOGIC_TYPE = "LIGHT";

var sensor_time = new Array();
var sensor_count = new Array();

function new_file(str) {
    return new FileWriter(LOGIC_TYPE.toLowerCase() + "-t" 
    + TOPOLOGY + "-a" + PYCO_NODE + str + ".txt");
}

function is_sensor_id()
{
  for (var i = 0; i <= SENSOR_NODE.length; i++) {
    if(id == SENSOR_NODE[i])
      return true;
  }
  return false;
}

function powerlog_init()
{
  powerlog_file = new_file("-P");
}

function powerlog_stop()
{
  powerlog_file.close();
}

function powerlog_write() 
{
  powerlog_file.write("ID:" + id + t + msg.toString() + "\n");
  powerlog_count++;
}

function init_eval()
{
  for (var i = 0; i <= SENSOR_NODE.length; i++) {
    sensor_time[i] = 0;
    sensor_count[i] = 0;
  }

  actuator_count = 0;
  powerlog_count = 0;
  num_samples = 0;
  sensor_id = -1;
  delay = -1;
  script_start_time = -1;
  script_end_time = -1;
  script_exec_time = -1

  file = new_file("-D");
  powerlog_init();
  t = "\t";
  mylog("\nSeed: " + sim.getRandomSeed() + "\n");
  print_topology();
  mylog(NUM_NODES + " nodes\n");
  mylog(LOGIC_TYPE + " with logic in node " + PYCO_NODE + "\n");
  mylog("#\tSensor\tDelay\tPF time\n");
  mylog("\tID\t[us]\t[us]\n");

  GENERATE_MSG(4000, "wait");
  YIELD_THEN_WAIT_UNTIL(msg.equals("wait"));
}

function end_eval()
{
  press_all_button();
  file.close();
  powerlog_stop();

  if (PYCO_NODE == LAST_PYCO_NODE)
    log.testOK();

  GENERATE_MSG(10000, "wait");
  YIELD_THEN_WAIT_UNTIL(msg.equals("wait"));
  press_all_button();
  YIELD_THEN_WAIT_UNTIL(msg.indexOf("Application") != -1);
  PYCO_NODE = id;
  init_eval();
}

function print_topology()
{
  mylog("Topology: ");
  switch(TOPOLOGY){
  case 0:
    mylog("STAR 1 with ");
    break;
  case 1:
    mylog("STAR 2 with ");
    break;
  case 2:
    mylog("STAR 3 with ");
    break;
  case 3:
    mylog("TREE 1 with ");
    break;
  case 4:
    mylog("TREE 2 with ");
    break;
  case 5:
    mylog("TREE 3 with ");
    break;
  case 6:
    mylog("TREE 4 with ");
    break;
  case 7:
    mylog("TREE 5 with ");
    break;
  case 8:
    mylog("TREE 6 with ");
    break;
  case 9:
    mylog("TREE 7 with ");
    break;
  case 10:
    mylog("MESH with ");
    break;
  default:
    mylog("ERROR - NO TOPOLOGY DEFINIED!!! STOP");
    log.testFailed();
    break;
  }
}

function mylog(str)
{
  log.log(str);
  file.write(str);
}

function press_all_button()
{
  for (var i = 1; i <= NUM_NODES; i++) {
    sim.getMoteWithID(i).getInterfaces().getButton().clickButton();
  }
}

plugin = mote.getSimulation().getGUI().
                          getStartedPlugin("se.sics.cooja.plugins.analyzers");

GENERATE_MSG(10000, "wait");
YIELD_THEN_WAIT_UNTIL(msg.equals("wait"));
press_all_button();
YIELD_THEN_WAIT_UNTIL(msg.indexOf("Application") != -1);
PYCO_NODE = id;
init_eval();

while (true) {

  if (is_sensor_id() && msg.indexOf("S: ") != -1 && sensor_id == -1) {
    sensor_id = id;
    sensor_time[id] = time;
    sensor_count[id]++;
    delay = -1;
    script_start_time = -1;
    script_end_time = -1;
  }
  
  if (id == PYCO_NODE && msg.equals("(-") && script_start_time == -1) {
    script_start_time = time;
  }
  
  if (id == PYCO_NODE && msg.equals("-)") && script_end_time == -1 ) {
    script_end_time = time;
  }
  
  if (id == ACTUATOR_NODE && msg.indexOf("A: ") != -1 && delay == -1) {
    delay = time - sensor_time[sensor_id];
    sensor_time[sensor_id] = 0;
    actuator_count++;
    script_exec_time = script_end_time - script_start_time;
    mylog((actuator_count) + t + sensor_id + t + delay + t + script_exec_time + "\n");
    sensor_id = -1;
  }

  if (msg.indexOf("P: ") != -1) {
    powerlog_write();
  }

  if(powerlog_count == NUM_POWERLOG_ENTRY){
    end_eval();
  }

  YIELD();
}
